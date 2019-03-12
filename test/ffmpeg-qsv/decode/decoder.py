###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(using_compatible_driver)
class DecoderTest(slash.Test):
  def before(self):
    self.refctx = []

  def decode(self):
    self.mformat = mapformat(self.format)
    if self.mformat is None:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    self.decoded = get_media()._test_artifact(
      "{case}_{width}x{height}_{format}.yuv".format(**vars(self)))

    self.output = call(
      "ffmpeg -hwaccel qsv -hwaccel_device /dev/dri/renderD128 -v verbose"
      " -c:v {ffdecoder} -i {source} -vf 'hwdownload,format={hwformat}'"
      " -pix_fmt {mformat} -f rawvideo -vsync passthrough"
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

    m = re.search("Initialize MFX session", self.output, re.MULTILINE)
    assert m is not None, "It appears that the QSV plugin did not load"

  def check_metrics(self):
    check_metric(**vars(self))
