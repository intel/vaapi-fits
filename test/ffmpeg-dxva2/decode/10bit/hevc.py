###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.ffmpeg.dxva2.util import *
from .....lib.ffmpeg.dxva2.decoder import DecoderTest

spec = load_test_spec("hevc", "decode", "10bit")

@slash.requires(*platform.have_caps("decode", "hevc_10"))
class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)
    self.caps   = platform.get_caps("decode", "hevc_10")
    super(default, self).before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    self.case = case
    self.decode()
