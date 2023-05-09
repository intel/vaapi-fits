###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash

from ...lib.common import timefn, get_media, call, exe2os, filepath2os
from ...lib.formats import match_best_format
from ...lib.gstreamer.util import have_gst, have_gst_element
from ...lib.gstreamer.util import parse_inline_md5, gst_discover_fps
from ...lib.parameters import format_value
from ...lib.util import skip_test_if_missing_features
from ...lib.properties import PropertyHandler

from ...lib import metrics2

class Decoder(PropertyHandler):
  #required properties
  gstdecoder  = property(lambda s: f" ! {s.props['gstdecoder']}")
  frames      = property(lambda s: s.props["frames"])
  format      = property(lambda s: s.props["format"])
  source      = property(lambda s: s.props["source"])
  ossource    = property(lambda s: filepath2os(s.source))
  decoded     = property(lambda s: s._decoded)
  osdecoded   = property(lambda s: filepath2os(s.decoded))

  #optional properties
  gstparser   = property(lambda s: s.ifprop("gstparser", " ! {gstparser}"))
  gstdemuxer  = property(lambda s: s.ifprop("gstdemuxer", " ! {gstdemuxer}"))

  #additional properties needed for some inline metrics
  width       = property(lambda s: s.props["width"])
  height      = property(lambda s: s.props["height"])
  statsfile   = property(lambda s: s._statsfile)
  osstatsfile = property(lambda s: filepath2os(s.statsfile))
  reference   = property(lambda s: s.props["reference"])
  osreference = property(lambda s: filepath2os(s.reference))

  @property
  def gstoutput(self):
    mtype = self.props.get("metric", dict()).get("type", None)

    if vars(self).get("_decoded", None) is not None:
      get_media()._purge_test_artifact(self._decoded)
    self._decoded = get_media()._test_artifact2("yuv")

    if vars(self).get("_statsfile", None) is not None:
      get_media()._purge_test_artifact(self._statsfile)
    self._statsfile = get_media()._test_artifact2(mtype)

    # WA: avvideocompare has some current limitations
    def can_inline_libav():
      return all([
        have_gst_element("avvideocompare")[0],
        "jpeg" not in self.gstdecoder,
      ])

    if "md5" == mtype:
      return (
        f"checksumsink2 qos=false eos-after={self.frames} file-checksum=false"
        f" frame-checksum=false plane-checksum=false dump-output=false"
      )
    elif mtype in ["psnr"] and can_inline_libav():
      fps = gst_discover_fps(self.ossource)
      return (
        f"avvideocompare method={mtype} stats-file={self.osstatsfile} name=cmp"
        f" ! fakevideosink qos=false num-buffers={self.frames} sync=0"
        f" filesrc location={self.osreference} num-buffers={self.frames}"
        f" ! rawvideoparse format={self.pformat} width={self.width}"
        f" height={self.height} framerate={fps} ! videoconvert chroma-mode=none"
        f" dither=0 ! video/x-raw,format={self.format} ! cmp."
      )

    return (
      f"checksumsink2 qos=false eos-after={self.frames}"
      f" file-checksum=false frame-checksum=false plane-checksum=false"
      f" dump-output=true dump-location={self.osdecoded}"
    )

  @timefn("gst:decode")
  def decode(self):
    return call(
      f"{exe2os('gst-launch-1.0')} -vf filesrc location={self.ossource}"
      f"{self.gstdemuxer}{self.gstparser}{self.gstdecoder}"
      f" ! videoconvert chroma-mode=none dither=0"
      f" ! video/x-raw,format={self.format} ! {self.gstoutput}"
    )

@slash.requires(have_gst)
@slash.requires(*have_gst_element("checksumsink2"))
class BaseDecoderTest(slash.Test):
  DecoderClass = Decoder

  def before(self):
    super().before()
    self.refctx = []
    self.post_validate = lambda: None

  def validate_caps(self):
    self.decoder = self.DecoderClass(**vars(self))

    if match_best_format(self.format, self.caps["fmts"]) is None:
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{format} not supported", **vars(self)))

    maxw, maxh = self.caps["maxres"]
    if self.width > maxw or self.height > maxh:
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{width}x{height} not supported", **vars(self)))

    if self.decoder.format is None:
      slash.skip_test(
        "gstreamer.{format} not supported".format(**vars(self)))

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

    self.check_metrics()

  def check_metrics(self):
    metric = metrics2.factory.create(**vars(self))
    if metric.__class__ is metrics2.md5.MD5:
      metric.actual = parse_inline_md5(self.output)
    else:
      metric.update(filetest = self.decoder.decoded)
    metric.check()
