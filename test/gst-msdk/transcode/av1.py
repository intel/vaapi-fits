###
### Copyright (C) 2024 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.msdk.util import *
from ....lib.gstreamer.msdk.transcoder import TranscoderTest
from ....lib.codecs import Codec

spec = load_test_spec("av1", "transcode")

class default(TranscoderTest):
  @slash.parametrize(("case"), sorted_by_resolution(spec))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case  = case,
      codec = Codec.AV1,
    )
    self.transcode()

