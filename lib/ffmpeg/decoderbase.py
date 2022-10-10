###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re
import slash

from ...lib.common import timefn, get_media, call, exe2os, filepath2os
from ...lib.ffmpeg.util import have_ffmpeg, BaseFormatMapper
from ...lib.ffmpeg.util import parse_inline_md5
from ...lib.parameters import format_value
from ...lib.util import skip_test_if_missing_features
from ...lib.properties import PropertyHandler

from ...lib import metrics2

class Decoder(PropertyHandler, BaseFormatMapper):
  # required properties
  frames    = property(lambda s: s.props["frames"])
  format    = property(lambda s: s.map_format(s.props["format"]))
  hwformat  = property(lambda s: s.map_best_hw_format(s.props["format"], s.props["caps"]["fmts"]))
  source    = property(lambda s: s.props["source"])
  ossource  = property(lambda s: filepath2os(s.source))
  decoded   = property(lambda s: s._decoded)
  osdecoded = property(lambda s: filepath2os(s.decoded))
  hwaccel   = property(lambda s: s.props["hwaccel"])
  hwdevice  = property(lambda s: get_media().render_device)

  # optional properties
  ffdecoder   = property(lambda s: s.ifprop("ffdecoder", "-c:v {ffdecoder}"))

  @property
  def scale_range(self):
    # NOTE: If test has requested scale in/out range, then apply it only when
    # hw and sw formats differ (i.e. when csc is necessary).
    if self.hwformat != self.format:
      return self.ifprop("ffscale_range",
        "-vf 'scale=in_range={ffscale_range}:out_range={ffscale_range}'")
    return ""

  @property
  def hwinit(self):
    return (
      f"-hwaccel {self.hwaccel}"
      f" -init_hw_device {self.hwaccel}=hw:{self.hwdevice}"
      f" -hwaccel_output_format {self.hwformat}"
      f" -hwaccel_flags allow_profile_mismatch"
    )

  @property
  def ffoutput(self):
    if self.props.get("metric", dict()).get("type", None) == "md5":
      return f"-f tee -map 0:v '{self.osdecoded}|[f=md5]pipe:1'"
    return f"{self.osdecoded}"

  @timefn("ffmpeg:decode")
  def decode(self):
    if vars(self).get("_decoded", None) is not None:
      get_media()._purge_test_artifact(self._decoded)
    self._decoded = get_media()._test_artifact2("yuv")

    return call(
      f"{exe2os('ffmpeg')} -v verbose {self.hwinit}"
      f" {self.ffdecoder} -i {self.ossource} {self.scale_range}"
      f" -c:v rawvideo -pix_fmt {self.format} -fps_mode passthrough"
      f" -autoscale 0 -vframes {self.frames} -y {self.ffoutput}"
    )

@slash.requires(have_ffmpeg)
class BaseDecoderTest(slash.Test, BaseFormatMapper):
  DecoderClass = Decoder

  def before(self):
    super().before()
    self.refctx = []
    self.post_validate = lambda: None

  def validate_caps(self):
    self.decoder = self.DecoderClass(**vars(self))

    if None in [self.decoder.hwformat, self.decoder.format]:
      slash.skip_test(f"{self.format} format not supported")

    maxw, maxh = self.caps["maxres"]
    if self.width > maxw or self.height > maxh:
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{width}x{height} not supported", **vars(self)))

    skip_test_if_missing_features(self)

    self.post_validate()

  def _decode_r2r(self):
    assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"

    vars(self).update(metric = dict(type = "md5"))
    self.decoder.update(metric = self.metric)

    metric = metrics2.factory.create(**vars(self))
    metric.actual = parse_inline_md5(self.decoder.decode())
    metric.expect = metric.actual # the first run is our reference for r2r
    metric.check()

    for i in range(1, self.r2r):
      metric.actual = parse_inline_md5(self.decoder.decode())
      metric.check()

  def decode(self):
    self.validate_caps()

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    if vars(self).get("r2r", None) is not None:
      return self._decode_r2r()

    self.output = self.decoder.decode()

    self.check_output()
    self.check_metrics()

  def check_output(self):
    m = re.search(
      "hwaccel initialisation returned error", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"

  def check_metrics(self):
    metric = metrics2.factory.create(**vars(self))
    if metric.__class__ is metrics2.md5.MD5:
      metric.actual = parse_inline_md5(self.output)
    else:
      metric.update(filetest = self.decoder.decoded)
    metric.check()
