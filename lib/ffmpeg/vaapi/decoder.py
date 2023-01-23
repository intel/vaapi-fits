###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re
import slash

from ....lib.common import get_media
from ....lib.ffmpeg.decoderbase import BaseDecoderTest, Decoder as FFDecoder
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel

class Decoder(FFDecoder):
  hwaccel = property(lambda s: "vaapi")

@slash.requires(*have_ffmpeg_hwaccel("vaapi"))
class DecoderTest(BaseDecoderTest):
  DecoderClass = Decoder

  def check_output(self):
    super().check_output()

    m = re.search(
      "Your platform doesn't support hardware accelerated .* decoding",
      self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"
