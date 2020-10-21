###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.decoder import DecoderTest

spec = load_test_spec("vp9", "decode", "8bit")

class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)
    self.caps   = platform.get_caps("decode", "vp9_8")
    super(default, self).before()

  @slash.requires(*platform.have_caps("decode", "vp9_8"))
  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    self.case = case
    self.decode()

  def check_output(self):
    m = re.search("No support for codec vp9", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"
    super(default, self).check_output()
