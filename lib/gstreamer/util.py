###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re

from ...lib.common import memoize, try_call, call, exe2os
from ...lib.formats import FormatMapper

def parse_inline_md5(msglog):
  return parse_inline_md5.pattern.search(msglog).group("actual")
parse_inline_md5.pattern = re.compile("md5 = (?P<actual>[0-9a-fA-F]{32})$", re.MULTILINE)

def parse_psnr_stats(filename, frames):
  from ...lib.ffmpeg.util import parse_psnr_stats as ffparse_psnr_stats
  return ffparse_psnr_stats(filename, frames)

@memoize
def have_gst():
  return try_call(f"which {exe2os('gst-launch-1.0')}") and try_call(f"which {exe2os('gst-inspect-1.0')}")

@memoize
def have_gst_element(element):
  result = try_call(f"{exe2os('gst-inspect-1.0')}"
                    " {}".format(element))
  return result, element

def gst_discover(filename):
  return call(f"{exe2os('gst-discoverer-1.0')}"
              " {}".format(filename))

def gst_discover_fps(filename):
  return gst_discover_fps.pattern.findall(gst_discover(filename))[-1]
gst_discover_fps.pattern = re.compile("Frame rate: (?P<fps>[0-9]+/[0-9]+)", re.MULTILINE)

@memoize
def get_elements(plugin):
  pattern = re.compile(f"element-(?P<element>.*)$", re.MULTILINE)
  result = ""
  try:
    result = call(f"{exe2os('gst-inspect-1.0')} --print-plugin-auto-install-info {plugin}")
  finally:
    return pattern.findall(result)

class BaseFormatMapper(FormatMapper):
  def get_supported_format_map(self):
    return {
      "I420"  : "I420",
      "NV12"  : "NV12",
      "YV12"  : "YV12",
      "AYUV"  : "VUYA", #we use microsoft's definition of AYUV,https://docs.microsoft.com/en-us/windows/win32/medfound/recommended-8-bit-yuv-formats-for-video-rendering#ayuv
      "YUY2"  : "YUY2",
      "ARGB"  : "ARGB",
      "BGRA"  : "BGRA",
      "422H"  : "Y42B",
      "444P"  : "Y444",
      "P010"  : "P010_10LE",
      "P012"  : "P012_LE",
      "I010"  : "I420_10LE",
      "Y210"  : "Y210",
      "Y212"  : "Y212_LE",
      "Y410"  : "Y410",
      "Y412"  : "Y412_LE",
    }
