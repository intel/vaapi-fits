###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re

from ...lib.common import memoize, try_call, call, exe2os

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
gst_discover_fps.pattern = re.compile("Frame rate: (?P<fps>[0-9]+)", re.MULTILINE)

@memoize
def get_elements(plugin):
  pattern = re.compile(f"element-(?P<element>.*)$", re.MULTILINE)
  result = ""
  try:
    result = call(f"{exe2os('gst-inspect-1.0')} --print-plugin-auto-install-info {plugin}")
  finally:
    return pattern.findall(result)
