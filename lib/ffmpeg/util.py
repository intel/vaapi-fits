###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ...lib.common import memoize, try_call, call, exe2os
from ...lib.formats import FormatMapper

@memoize
def have_ffmpeg():
  return try_call(f"which {exe2os('ffmpeg')}")

@memoize
def have_ffmpeg_hwaccel(accel):
  result = try_call(f"{exe2os('ffmpeg')} -hide_banner -hwaccels | grep {accel}")
  return result, accel

@memoize
def have_ffmpeg_filter(name):
  result = try_call(f"{exe2os('ffmpeg')} -hide_banner -filters | awk '{{print $2}}' | grep -w {name}")
  return result, name

@memoize
def have_ffmpeg_encoder(encoder):
  result = try_call(f"{exe2os('ffmpeg')} -hide_banner -encoders | awk '{{print $2}}' | grep -w {encoder}")
  return result, encoder

@memoize
def have_ffmpeg_decoder(decoder):
  result = try_call(f"{exe2os('ffmpeg')} -hide_banner -decoders | awk '{{print $2}}' | grep -w {decoder}")
  return result, decoder

def ffmpeg_probe_resolution(filename):
  return call(
    f"{exe2os('ffprobe')} -v quiet -select_streams v:0"
    " -show_entries stream=width,height -of"
    f" csv=s=x:p=0 {filename}"
  ).strip().strip('x')

class BaseFormatMapper(FormatMapper):
  def get_supported_format_map(self):
    return {
      "I420"  : "yuv420p",
      "NV12"  : "nv12",
      "P010"  : "p010le",
      "P012"  : "p012",
      "I010"  : "yuv420p10le",
      "YUY2"  : "yuyv422",
      "422H"  : "yuv422p",
      "422V"  : "yuv440p",
      "444P"  : "yuv444p",
      "Y800"  : "gray8",
      "ARGB"  : "rgb32",
      "BGRA"  : "bgra",
      "Y210"  : "y210",
      "Y212"  : "y212",
      "Y410"  : "y410",
      "Y412"  : "y412",
      "AYUV"  : "vuya", # vuya is same as microsoft AYUV except the alpha channel
    }
