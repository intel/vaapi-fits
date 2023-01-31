###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import re
import slash

from ...lib.common import timefn, get_media, call, exe2os, filepath2os
from ...lib.gstreamer.util import have_gst, have_gst_element, parse_inline_md5
from ...lib.gstreamer.decoderbase import Decoder
from ...lib.parameters import format_value
from ...lib.util import skip_test_if_missing_features
from ...lib.properties import PropertyHandler

from ...lib import metrics2

class Encoder(PropertyHandler):
  # required properties
  gstencoder    = property(lambda s: s.props["gstencoder"])
  gstmediatype  = property(lambda s: s.props["gstmediatype"])
  codec         = property(lambda s: s.props["codec"])
  rcmode        = property(lambda s: s.props["rcmode"])
  hwformat      = property(lambda s: s.props["hwformat"])
  format        = property(lambda s: s.props["format"])
  frames        = property(lambda s: s.props["frames"])
  width         = property(lambda s: s.props["width"])
  height        = property(lambda s: s.props["height"])
  source        = property(lambda s: s.props["source"])
  ossource      = property(lambda s: filepath2os(s.source))
  encoded       = property(lambda s: s._encoded)
  osencoded     = property(lambda s: filepath2os(s.encoded))
  encoded_ext   = property(lambda s: s.props["encoded_ext"])

  # optional properties
  gstparser     = property(lambda s: s.ifprop("gstparser", " ! {gstparser}"))
  gstmuxer      = property(lambda s: s.ifprop("gstmuxer", " ! {gstmuxer}"))
  fps           = property(lambda s: s.ifprop("fps", " framerate={fps}"))
  profile       = property(lambda s: s.ifprop("profile", ",profile={profile}"))

  @property
  def lowpower(self):
    def inner(lowpower):
      return f" tune={'low-power' if lowpower else 'none'}"
    return self.ifprop("lowpower", inner)

  @property
  def gstoutput(self):
    if self.props.get("metric", dict()).get("type", None) == "md5":
      # gstreamer muxers write timestamps to container header and produce
      # a different md5 each time.  Thus, don't use the muxer when checking
      # md5.
      return " ! testsink sync=false"
    return f"{self.gstmuxer} ! filesink location={self.osencoded}"

  @timefn("gst:encode")
  def encode(self):
    if vars(self).get("_encoded", None) is not None:
      get_media()._purge_test_artifact(self._encoded)
    self._encoded = get_media()._test_artifact2(f"{self.encoded_ext}")

    return call(
      f"{exe2os('gst-launch-1.0')} -vf filesrc location={self.ossource} num-buffers={self.frames}"
      f" ! rawvideoparse format={self.format} width={self.width} height={self.height}{self.fps}"
      f" ! videoconvert chroma-mode=none dither=0 ! video/x-raw,format={self.hwformat}"
      f" ! {self.gstencoder} ! {self.gstmediatype}{self.profile}{self.gstparser}"
      f"{self.gstoutput}"
    )

@slash.requires(have_gst)
@slash.requires(*have_gst_element("checksumsink2"))
class BaseEncoderTest(slash.Test):
  EncoderClass = Encoder
  DecoderClass = Decoder

  def before(self):
    super().before()
    self.refctx = []
    self.post_validate = lambda: None

  def map_profile(self):
    raise NotImplementedError

  def get_file_ext(self):
    raise NotImplementedError

  def validate_caps(self):
    skip_test_if_missing_features(self)

    self.encoder = self.EncoderClass(encoded_ext = self.get_file_ext(), **vars(self))
    self.decoder = self.DecoderClass(
      gstdecoder  = self.gstdecoder,
      gstparser   = vars(self).get("gstparser", None),
      gstdemuxer  = vars(self).get("gstdemuxer", None),
      frames      = self.frames,
      format      = self.format,
    )

    if None in [self.encoder.hwformat, self.encoder.format, self.decoder.format]:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    maxw, maxh = self.caps["maxres"]
    if self.width > maxw or self.height > maxh:
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{width}x{height} not supported", **vars(self)))

    if vars(self).get("slices", 1) > 1 and not self.caps.get("multislice", True):
      slash.skip_test(
        format_value(
          "{platform}.{driver}.slice > 1 unsupported in this mode", **vars(self)))

    if not self.caps.get(self.rcmode, True):
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{rcmode} unsupported in this mode", **vars(self)))

    if vars(self).get("profile", None) is not None:
      self.mprofile = self.map_profile()
      if self.mprofile is None:
        slash.skip_test("{profile} profile is not supported".format(**vars(self)))
      self.encoder.update(profile = self.mprofile)

    self.post_validate()

  def _encode_r2r(self):
    assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"

    vars(self).update(metric = dict(type = "md5"))
    self.encoder.update(metric = self.metric)

    metric = metrics2.factory.create(**vars(self))
    metric.actual = parse_inline_md5(self.encoder.encode())
    metric.expect = metric.actual # the first run is our reference for r2r
    metric.check()

    for i in range(1, self.r2r):
      metric.actual = parse_inline_md5(self.encoder.encode())
      metric.check()

  def encode(self):
    self.validate_caps()

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    if vars(self).get("r2r", None) is not None:
      return self._encode_r2r()

    self.encoder.encode()

    self.check_bitrate()
    self.check_max_frame_size()
    self.check_metrics()

  def check_metrics(self):
    self.decoder.update(source = self.encoder.encoded)
    self.decoder.decode()

    metrics2.factory.create(
      metric = dict(type = "psnr"),
      filetrue = self.source, filetest = self.decoder.decoded,
      width = self.width, height = self.height, frames = self.frames,
      format = self.format, refctx = self.refctx
    ).check()

  def check_bitrate(self):
    encsize = os.path.getsize(self.encoder.encoded)
    bitrate_actual = encsize * 8 * vars(self).get("fps", 25) / 1024.0 / self.frames
    get_media()._set_test_details(
      size_encoded = encsize,
      bitrate_actual = "{:-.2f}".format(bitrate_actual))

    if "cbr" == self.rcmode:
      bitrate_gap = abs(bitrate_actual - self.bitrate) / self.bitrate
      get_media()._set_test_details(bitrate_gap = "{:.2%}".format(bitrate_gap))

      # acceptable bitrate within 10% of bitrate
      assert(bitrate_gap <= 0.10)

    elif self.rcmode in ["vbr", "la_vbr"] and vars(self).get("maxframesize", None) is None:
      # acceptable bitrate within 25% of minrate and 10% of maxrate
      assert(self.minrate * 0.75 <= bitrate_actual <= self.maxrate * 1.10)

  def check_max_frame_size(self):
    if vars(self).get("maxframesize", None) is None:
      return

    output = call(
      f"{exe2os('gst-launch-1.0')} -vf filesrc location={self.encoder.encoded}"
      f" ! {self.gstparser} ! {self.gstmediatype},alignment=au"
      f" ! identity silent=false ! fakesink"
    )

    actual = re.findall(r'(?<=identity0:sink\) \().[0-9]*', output)
    assert len(actual) == self.frames, "Probe failed for frame sizes"

    target = self.maxframesize * 1000 # kbytes -> bytes
    results = [int(sz) <= target for sz in actual]
    failed = results.count(False)
    rate = failed / len(results)

    get_media()._set_test_details(**{
      "frame:size:target (bytes)" : f"{target:0.2f}",
      "frame:size:failed" : f"{failed} ({rate:0.2%})",
    })

    assert rate < 0.2, "Too many frames exceed target/max frame size"
