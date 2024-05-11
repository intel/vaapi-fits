###
### Copyright (C) 2024 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.d3d12.util import *
from ....lib.gstreamer.d3d12.decoder import AVCDecoderTest as DecoderTest

spec = load_test_spec("avc", "decode")

class default(DecoderTest):
  def before(self):
    super().before()
    vars(self).update(
      # default metric
      metric      = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0),
    )

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case)
    self.decode()
