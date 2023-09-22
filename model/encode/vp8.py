###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ...lib.ffmpeg.vaapi.util import *
from ...lib.ffmpeg.vaapi.encoder import VP8EncoderTest
from .util import TrendModelMixin

spec = load_test_spec("vp8", "encode")

class trend(VP8EncoderTest, TrendModelMixin):
  #MRO overrides
  check_metrics = TrendModelMixin.check_metrics

  def parse_psnr(self):
    if os.path.exists(self.decoder.statsfile):
      return parse_psnr_stats(self.decoder.statsfile, self.frames)

  def initvars(self, _):
    super().initvars("version0_3")

  @slash.parametrize(*TrendModelMixin.filter_spec(spec))
  def test(self, case):
    vars(self).update(case = case, ffencoder = self.ffenc)
    vars(self).update(
      modelqps = range(1, 128, 6),
      modelfns = ["powernc", "powerc", "powern", "power"], # don't use cubic
    )
    vars(self).update(spec[case].copy())
    self.fit()
  
  def check_output(self):
    pass
