###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ...lib.ffmpeg.qsv.util import *
from ...lib.ffmpeg.qsv.encoder import HEVC8EncoderTest
from .util import TrendModelMixin

spec = load_test_spec("hevc", "encode", "8bit")

class trend(HEVC8EncoderTest, TrendModelMixin):
  #MRO overrides
  check_metrics = TrendModelMixin.check_metrics

  def parse_psnr(self):
    if os.path.exists(self.decoder.statsfile):
      return parse_psnr_stats(self.decoder.statsfile, self.frames)

  def initvars(self, _):
    profile = "main"
    if "AYUV" == self.format:
      profile = "main444"
    if "YUY2" == self.format:
      profile = "main422"
    if "scc" in vars(self).get("features", []):
      profile = "scc"
      if "AYUV" == self.format:
        profile = "scc-444"
    elif "msp" in vars(self).get("features", []):
      profile = "mainsp"

    super().initvars(profile)

  @slash.parametrize(*TrendModelMixin.filter_spec(spec))
  def test(self, case):
    vars(self).update(case = case)
    vars(self).update(spec[case].copy())

    # Some features/formats are only supported by VDENC (lowpower = 1).
    # Thus, don't pass the lowpower mode to the command-line explicitly.
    # This lets the underlying encoder plugin decide what to do.
    del self.lowpower

    self.fit()

  def check_output(self):
    # Ignore output checks for now to avoid VME/VDENC check.
    pass
