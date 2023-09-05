###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.ffmpeg.qsv.util import *
from ....lib.ffmpeg.qsv.encoder import HEVC12EncoderTest
from ..util import TrendModelMixin

spec = load_test_spec("hevc", "encode", "12bit")

class trend(HEVC12EncoderTest, TrendModelMixin):
  #MRO overrides
  check_metrics = TrendModelMixin.check_metrics

  def parse_psnr(self):
    if os.path.exists(self.decoder.statsfile):
      return parse_psnr_stats(self.decoder.statsfile, self.frames)

  def initvars(self, _):
    profile = "main12"
    if "Y212" == self.format:
      profile = "main422-12"
    super().initvars(profile)

  @slash.parametrize(*TrendModelMixin.filter_spec(spec))
  def test(self, case):
    vars(self).update(case = case)
    vars(self).update(spec[case].copy())

    self.fit()
