###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.d3d12.util import *
from ....lib.ffmpeg.d3d12.decoder import DecoderTest

spec = load_test_spec("av1", "decode", "8bit")

@slash.requires(*platform.have_caps("decode", "av1_8"))
class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)
    self.caps   = platform.get_caps("decode", "av1_8")
    super(default, self).before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    self.case = case
    self.decode()
