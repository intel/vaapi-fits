###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash

from ....lib.common import get_media
from ....lib.ffmpeg.decoderbase import BaseDecoderTest, Decoder as FFDecoder
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel

class Decoder(FFDecoder):
  hwaccel = property(lambda s: "dxva2")

  def get_supported_format_map(self):
    return {
      "I420"  : "yuv420p",
      "NV12"  : "nv12",
      "P010"  : "p010le",
    }

@slash.requires(*have_ffmpeg_hwaccel("dxva2"))
class DecoderTest(BaseDecoderTest):
  DecoderClass = Decoder
