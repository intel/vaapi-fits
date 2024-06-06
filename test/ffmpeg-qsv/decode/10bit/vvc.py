###
### Copyright (C) 2024 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.ffmpeg.qsv.util import *
from .....lib.ffmpeg.qsv.decoder import DecoderTest

spec = load_test_spec("vvc", "decode", "10bit")

@slash.requires(*platform.have_caps("decode", "vvc_10"))
@slash.requires(*have_ffmpeg_decoder("vvc_qsv"))
class default(DecoderTest):
  def before(self):
    # default metric
    vars(self).update(
      caps        = platform.get_caps("decode", "vvc_10"),
      ffdecoder   = "vvc_qsv",
      metric      = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0),
    )
    super().before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    self.case = case
    self.decode()
