###
### Copyright (C) 2024 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.d3d12.util import *
from ....lib.gstreamer.d3d12.decoder import MPEG2DecoderTest as DecoderTest

spec = load_test_spec("mpeg2", "decode")
spec_r2r = load_test_spec("mpeg2", "decode", "r2r")

class default(DecoderTest):
  def before(self):
    super().before()
    vars(self).update(
      # default metric
      metric      = dict(type = "ssim", miny = 0.99, minu = 0.99, minv = 0.99),
    )

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case)
    self.decode()

  @slash.parametrize(("case"), sorted(spec_r2r.keys()))
  def test_r2r(self, case):
    vars(self).update(spec_r2r[case].copy())
    vars(self).update(case = case)
    vars(self).setdefault("r2r", 5)
    self.decode()
