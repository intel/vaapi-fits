###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .transcoder import TranscoderTest

spec = load_test_spec("hevc", "transcode")

class default(TranscoderTest):
  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case  = case,
      codec = "hevc",
    )
    self.transcode()
