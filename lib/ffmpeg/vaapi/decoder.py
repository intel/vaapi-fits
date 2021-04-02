###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from .util import *

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
class DecoderTest(slash.Test):
  def before(self):
    self.refctx = []
    self.renderDevice = get_media().render_device

  @timefn("ffmpeg")
  def call_ffmpeg(self):
    self.output = call(
      "ffmpeg -hwaccel vaapi -init_hw_device vaapi=hw:{renderDevice}"
      " -hwaccel_flags allow_profile_mismatch -filter_hw_device hw -v verbose"
      " -i {source} -pix_fmt {mformat} -f rawvideo -vsync passthrough"
      " -autoscale 0 -vframes {frames} -y {decoded}".format(**vars(self)))

  def gen_name(self):
    name = "{case}_{width}x{height}_{format}"
    if vars(self).get("r2r", None) is not None:
      name += "_r2r"
    return name

  def validate_caps(self):
    if match_best_format(self.format, self.caps["fmts"]) is None:
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{format} not supported", **vars(self)))

    maxw, maxh = self.caps["maxres"]
    if self.width > maxw or self.height > maxh:
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{width}x{height} not supported", **vars(self)))

    self.mformat = mapformat(self.format)
    if self.mformat is None:
      slash.skip_test(
        "ffmpeg.{format} format not supported".format(**vars(self)))

    skip_test_if_missing_features(self)

  def decode(self):
    self.validate_caps()

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    name = self.gen_name().format(**vars(self))
    self.decoded = get_media()._test_artifact("{}.yuv".format(name))
    self.call_ffmpeg()

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = md5(self.decoded)
      get_media()._set_test_details(md5_ref = md5ref)
      for i in range(1, self.r2r):
        self.decoded = get_media()._test_artifact("{}_{}.yuv".format(name, i))
        self.call_ffmpeg()
        result = md5(self.decoded)
        get_media()._set_test_details(**{"md5_{:03}".format(i) : result})
        assert result == md5ref, "r2r md5 mismatch"
        # delete decoded file after each iteration
        get_media()._purge_test_artifact(self.decoded)
    else:
      self.check_output()
      self.check_metrics()

  def check_output(self):
    m = re.search(
      "hwaccel initialisation returned error", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"

  def check_metrics(self):
    check_metric(**vars(self))
