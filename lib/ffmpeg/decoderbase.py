###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re
import slash

from ...lib.artifacts import Scope
from ...lib.common import timefn, get_media, call, exe2os, filepath2os
from ...lib.ffmpeg.util import have_ffmpeg, ffmpeg_probe_fps, BaseFormatMapper
from ...lib.ffmpeg.util import parse_inline_md5, parse_ssim_stats, parse_psnr_stats
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

  # optional properties
  ffdecoder   = property(lambda s: s.ifprop("ffdecoder", "-c:v {ffdecoder}"))

  width       = property(lambda s: s.props["width"])
  height      = property(lambda s: s.props["height"])
  statsfile   = property(lambda s: s._statsfile)
  osstatsfile = property(lambda s: filepath2os(s.statsfile))
  reference   = property(lambda s: s.props["reference"])
  osreference = property(lambda s: filepath2os(s.reference))

  def __init__(self, scope = Scope.TEST, **properties):
    super().__init__(**properties)
    self._scope = scope

  @property
  def scale_range(self):
    return self.ifprop("ffscale_range",
      "scale=in_range={ffscale_range}:out_range={ffscale_range}") or "null"

  @property
  def hwdevice(self):
    return f'hw:{get_media().render_device}'

  @property
  def hwinit(self):
    return (
      f"-hwaccel {self.hwaccel}"
      f" -init_hw_device {self.hwaccel}={self.hwdevice}"
      f" -hwaccel_output_format {self.hwformat}"
      f" -hwaccel_flags allow_profile_mismatch"
    )

  @property
  def ffoutput(self):
    if self.props.get("metric", dict()).get("type", None) == "md5":
      return f"-f tee '[f=md5]pipe:1'"
    return f"{self.osdecoded}"

  @timefn("ffmpeg:decode")
  def decode(self):
    if vars(self).get("_decoded", None) is not None:
      get_media().artifacts.purge(self._decoded, self._scope)
    self._decoded = get_media().artifacts.reserve("yuv", self._scope)

    mtype = self.props.get("metric", dict()).get("type", None)
    if mtype in ["ssim", "psnr"]:
      fps = ffmpeg_probe_fps(self.ossource)

      if vars(self).get("_statsfile", None) is not None:
        get_media().artifacts.purge(self._statsfile)
      self._statsfile = get_media().artifacts.reserve(mtype)

      return call(
        f"{exe2os('ffmpeg')} -v verbose {self.hwinit}"
        f" {self.ffdecoder} -r:v {fps} -i {self.ossource}"
        f" -f rawvideo -pix_fmt {self.format} -s:v {self.width}x{self.height}"
        f" -r:v {fps} -i {self.osreference}"
        f" -lavfi \"{self.scale_range},{mtype}=f=\\'{self.osstatsfile}\\':shortest=1\""
        f" -fps_mode passthrough -noautoscale -vframes {self.frames} -f null -"
      )

    return call(
      f"{exe2os('ffmpeg')} -v verbose {self.hwinit}"
      f" {self.ffdecoder} -i {self.ossource} -lavfi '{self.scale_range}'"
      f" -c:v rawvideo -pix_fmt {self.format} -fps_mode passthrough"
      f" -noautoscale -vframes {self.frames} -y {self.ffoutput}"
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
    metric.update(filetest = self.decoder.decoded)

    if metric.__class__ is metrics2.md5.MD5:
      metric.actual = parse_inline_md5(self.output)
    elif metric.__class__ is metrics2.ssim.SSIM:
      metric.actual = parse_ssim_stats(self.decoder.statsfile, self.frames)
    elif metric.__class__ is metrics2.ssim.PSNR:
      metric.actual = parse_psnr_stats(self.decoder.statsfile, self.frames)

    metric.check()
