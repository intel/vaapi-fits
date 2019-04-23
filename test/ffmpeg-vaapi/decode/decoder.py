###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
class DecoderTest(slash.Test):
  def before(self):
    self.refctx = []

  def decode(self):
    self.mformat = mapformat(self.format)
    if self.mformat is None:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    self.decoded = get_media()._test_artifact(
      "{case}_{width}x{height}_{format}.yuv".format(**vars(self)))

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    self.output = call(
      "ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -v debug"
      " -i {source} -pix_fmt {mformat} -f rawvideo -vsync passthrough"
      " -vframes {frames} -y {decoded}".format(**vars(self)))

    self.check_output()
    self.check_metrics()

  def check_output(self):
    m = re.search(
      "not supported for hardware decode", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"

    m = re.search(
      "hwaccel initialisation returned error", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"

    m = re.search( # this requires ffmpeg debug verbosity
      "Format vaapi_vld chosen by get_format", self.output, re.MULTILINE)
    assert m is not None, "Failed to choose vaapi_vld decode format"

  def check_metrics(self):
    check_metric(**vars(self))
