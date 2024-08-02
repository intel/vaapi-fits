###
### Copyright (C) 2024 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.decoder import VVC_8DecoderTest as DecoderTest

spec = load_test_spec("vvc", "decode", "8bit")

class default(DecoderTest):
  def before(self):
    # default metric
    vars(self).update(
      metric      = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0),
    )
    super().before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    self.case = case
    self.decode()
