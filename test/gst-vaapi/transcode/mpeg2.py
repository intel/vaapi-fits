##
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.codecs import Codec
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.transcoder import TranscoderTest

spec = load_test_spec("mpeg2", "transcode")

class default(TranscoderTest):
  @slash.parametrize(("case"), sorted_by_resolution(spec))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case  = case,
      codec = Codec.MPEG2,
    )
    self.transcode()
