###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

__scalers__ = {
  "hw"  : lambda: "-vf 'hwupload,scale_vaapi=w={width}:h={height}:mode=fast,hwdownload,format=nv12'",
  "sw"  : lambda: "-s:v {width}x{height}",
  True  : lambda: __scalers__["sw"](),
}

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
class DecoderTest(slash.Test):
  def before(self):
    self.refctx = []

  @timefn("ffmpeg")
  def call_ffmpeg(self):
    self.output = call(
      "ffmpeg -hwaccel vaapi -init_hw_device vaapi=hw:/dev/dri/renderD128"
      " -filter_hw_device hw -v verbose"
      " -i {source} {ffscaler} -pix_fmt {mformat} -f rawvideo -vsync"
      " passthrough -vframes {frames} -y {decoded}".format(**vars(self)))

  def gen_name(self):
    name = "{case}_{width}x{height}_{format}"
    if vars(self).get("r2r", None) is not None:
      name += "_r2r"
    return name

  def decode(self):
    self.mformat = mapformat(self.format)

    if self.mformat is None:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    self.ffscaler = __scalers__.get(
      vars(self).get("scale_output", False), lambda: "")().format(**vars(self))
    name = self.gen_name().format(**vars(self))
    self.decoded = get_media()._test_artifact("{}.yuv".format(name))
    self.call_ffmpeg()

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = md5(self.decoded)
      get_media()._set_test_details(md5_ref = md5ref)
      for i in xrange(1, self.r2r):
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
      "not supported for hardware decode", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"

    m = re.search(
      "hwaccel initialisation returned error", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"

  def check_metrics(self):
    check_metric(**vars(self))
