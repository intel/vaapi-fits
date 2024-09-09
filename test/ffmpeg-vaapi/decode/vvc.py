###
### Copyright (C) 2024 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.decoder import DecoderTest

spec = load_test_spec("vvc", "decode", "8bit")

@slash.requires(*platform.have_caps("decode", "vvc_8"))
@slash.requires(*have_ffmpeg_decoder("vvc"))
class default(DecoderTest):
  def before(self):
    vars(self).update(
      caps        = platform.get_caps("decode", "vvc_8"),
      ffdecoder   = "vvc",
      metric      = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0), # default metric
    )
    super().before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    self.case = case
    self.decode()
