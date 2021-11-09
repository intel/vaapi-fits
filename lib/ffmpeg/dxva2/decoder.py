###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash

from ....lib.common import get_media
from ....lib.ffmpeg.decoderbase import BaseDecoderTest
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel

@slash.requires(*have_ffmpeg_hwaccel("dxva2"))
class DecoderTest(BaseDecoderTest):
  def before(self):
    super().before()
    self.hwaccel = "dxva2"
