###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash

from ....lib.common import get_media
from ....lib.ffmpeg.decoderbase import BaseDecoderTest
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel

@slash.requires(*have_ffmpeg_hwaccel("d3d11va"))
class DecoderTest(BaseDecoderTest):
  def before(self):
    super().before()
    self.hwaccel = "d3d11va"

  def get_supported_format_map(self):
    return {
      "I420"  : "yuv420p",
      "NV12"  : "nv12",
      "P010"  : "p010le",
    }
