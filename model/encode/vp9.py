###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ...lib.ffmpeg.qsv.util import *
from ...lib.ffmpeg.qsv.encoder import VP9_8EncoderLPTest
from .util import TrendModelMixin

spec = load_test_spec("vp9", "encode", "8bit")

class trend(VP9_8EncoderLPTest, TrendModelMixin):
  #MRO overrides
  check_metrics = TrendModelMixin.check_metrics

  def parse_psnr(self):
    if os.path.exists(self.decoder.statsfile):
      return parse_psnr_stats(self.decoder.statsfile, self.frames)

  def initvars(self, _):
    profile = "profile0"
    if "AYUV" == self.format:
      profile = "profile1"

    super().initvars(profile)

  @slash.parametrize(*TrendModelMixin.filter_spec(spec))
  def test(self, case):
    vars(self).update(case = case)
    vars(self).update(
      modelqps = list(range(1, 11, 2))
        + list(range(11, 247, 30))
        + list(range(247, 256, 2))
    )
    vars(self).update(spec[case].copy())
    self.fit()
  
  def check_output(self):
    # Ignore output checks for now to avoid VME/VDENC check.
    pass
