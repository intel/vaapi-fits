###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib.common import memoize, get_media
from ....lib.ffmpeg.util import *

def using_compatible_driver():
  return get_media()._get_driver_name() in ["iHD", "d3d11", "dxva2"]

def have_encode_main10sp(encoder):
  return try_call(f"{exe2os('ffmpeg')} -hide_banner -h encoder={encoder} | grep '\\-main10sp'")

@memoize
def map_deinterlace_method(method):
  return {
    "bob"               : "bob",
    "motion-adaptive"   : "advanced", # aka
    "advanced"          : "advanced",
  }.get(method, None)

@memoize
def map_transpose_direction(degrees, method):
  return {
    (  0,   "vertical") : "vflip",
    (  0, "horizontal") : "hflip",
    ( 90,         None) : "clock",
    ( 90,   "vertical") : "cclock_hflip",
    ( 90, "horizontal") : "clock_hflip",
    (180,         None) : "reversal",
    (180,   "vertical") : "hflip",
    (180, "horizontal") : "vflip",
    (270,         None) : "cclock",
    (270,   "vertical") : "clock_hflip",
    (270, "horizontal") : "cclock_hflip",
  }.get( (degrees, method), None)

@memoize
def mapprofile(codec, profile):
  return {
    "avc"      : {
      "high"      : "high",
      "main"      : "main",
      "baseline"  : "baseline",
      "unknown"   : "unknown"
    },
    "hevc-8"   : {
      "main"      : "main",
      "main444"   : "rext",
      "scc"       : "scc",
      "scc-444"   : "scc",
      "mainsp"    : "mainsp",
      "unknown"   : "unknown"
    },
    "hevc-10"  : {
      "main10"     : "main10",
      "main10sp"   : "main10 -main10sp 1",
      "main444-10" : "rext"
    },
    "hevc-12" : {
      "main12"      : "rext",
      "main422-12"  : "rext",
    },
    "av1-8"   : {
      "profile0"  : "main",
    },
    "av1-10"   : {
      "profile0"  : "main",
    },
    "vp9-12" : {
      "profile3"  : "profile3",
    },
  }.get(codec, {}).get(profile, None)

def load_test_spec(*ctx):
  from ....lib import util as libutil
  return libutil.load_test_spec("ffmpeg-qsv", *ctx)
