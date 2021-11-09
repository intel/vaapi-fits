###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.dxva2.util import *
from ....lib.ffmpeg.dxva2.decoder import DecoderTest

spec = load_test_spec("mpeg2", "decode")
spec_r2r = load_test_spec("mpeg2", "decode", "r2r")

@slash.requires(*platform.have_caps("decode", "mpeg2"))
class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 0.99, minu = 0.99, minv = 0.99)
    self.caps   = platform.get_caps("decode", "mpeg2")
    super(default, self).before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    self.case = case
    self.decode()

  @slash.parametrize(("case"), sorted(spec_r2r.keys()))
  def test_r2r(self, case):
    vars(self).update(spec_r2r[case].copy())
    vars(self).setdefault("r2r", 5)
    self.case = case
    self.decode()
