###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import enum

@enum.unique
class Codec(str, enum.Enum):
  NONE  = "none"
  RAW   = "raw"
  AVC   = "avc"
  HEVC  = "hevc"
  AV1   = "av1"
  VP9   = "vp9"
  VP8   = "vp8"
  JPEG  = "jpeg"
  MJPEG = "mjpeg"
  MPEG2 = "mpeg2"
  VC1   = "vc1"
  VVC   = "vvc"
  def __str__(self):
    return self.value
