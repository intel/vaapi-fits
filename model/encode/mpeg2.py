###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ...lib.ffmpeg.qsv.util import *
from ...lib.ffmpeg.qsv.encoder import MPEG2EncoderTest
from .util import TrendModelMixin

spec = load_test_spec("mpeg2", "encode")

class trend(MPEG2EncoderTest, TrendModelMixin):
  # MRO overrides
  check_metrics = TrendModelMixin.check_metrics

  def parse_psnr(self):
    if os.path.exists(self.decoder.statsfile):
      return parse_psnr_stats(self.decoder.statsfile, self.frames)

  @slash.parametrize(*TrendModelMixin.filter_spec(spec))
  def test(self, case):
    vars(self).update(case = case)
    vars(self).update(
      # don't include cubic by default
      modelfns = ["powernc", "powerc", "powern", "power"],
      modelqps = range(1, 101, 3),
    )
    vars(self).update(spec[case].copy())
    self.fit()
