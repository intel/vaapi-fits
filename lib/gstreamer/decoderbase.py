###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash

from ...lib.common import timefn, get_media, call, exe2os, filepath2os
from ...lib.formats import match_best_format
from ...lib.gstreamer.util import have_gst, have_gst_element
from ...lib.parameters import format_value
from ...lib.util import skip_test_if_missing_features
from ...lib.metrics import md5, check_metric
from ...lib.properties import PropertyHandler

class Decoder(PropertyHandler):
  #required properties
  gstdecoder  = property(lambda s: f" ! {s.props['gstdecoder']}")
  frames      = property(lambda s: s.props["frames"])
  format      = property(lambda s: s.props["format"])
  source      = property(lambda s: s.props["source"])
  decoded     = property(lambda s: s.props["decoded"])

  #optional properties
  gstparser   = property(lambda s: s.ifprop("gstparser", " ! {gstparser}"))
  gstdemuxer  = property(lambda s: s.ifprop("gstdemuxer", " ! {gstdemuxer}"))

  @timefn("gst-decode")
  def decode(self):
    return call(
      f"{exe2os('gst-launch-1.0')} -vf filesrc location={filepath2os(self.source)}"
      f"{self.gstdemuxer}{self.gstparser}{self.gstdecoder}"
      f" ! videoconvert chroma-mode=none dither=0"
      f" ! video/x-raw,format={self.format} ! checksumsink2 qos=false"
      f" file-checksum=false frame-checksum=false plane-checksum=false"
      f" eos-after={self.frames} dump-output=true dump-location={filepath2os(self.decoded)}"
    )

@slash.requires(have_gst)
@slash.requires(*have_gst_element("checksumsink2"))
class BaseDecoderTest(slash.Test):
  DecoderClass = Decoder

  def before(self):
    super().before()
    self.refctx = []
    self.post_validate = lambda: None

  def gen_name(self):
    name = "{case}_{width}x{height}_{format}"
    if vars(self).get("r2r", None) is not None:
      name += "_r2r"
    return name

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

  def decode(self):
    self.validate_caps()

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    name = self.gen_name().format(**vars(self))
    self.decoder.update(
      decoded = get_media()._test_artifact("{}.yuv".format(name)))
    self.output = self.decoder.decode()

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = md5(self.decoder.decoded)
      get_media()._set_test_details(md5_ref = md5ref)
      for i in range(1, self.r2r):
        self.decoder.update(
          decoded = get_media()._test_artifact("{}_{}.yuv".format(name, i)))
        self.decoder.decode()
        result = md5(self.decoder.decoded)
        get_media()._set_test_details(**{"md5_{:03}".format(i): result})
        assert result == md5ref, "r2r md5 mismatch"
        # delete decoded file after each iteration
        get_media()._purge_test_artifact(self.decoder.decoded)
    else:
      self.decoded = self.decoder.decoded
      self.check_metrics()

  def check_metrics(self):
    check_metric(**vars(self))
