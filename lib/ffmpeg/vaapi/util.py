###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib.common import memoize
from ....lib.ffmpeg.util import *
from ....lib.codecs import Codec

@memoize
def map_deinterlace_method(method):
  from ....lib import get_media
  return {
    "iHD" : {
      "bob"               : "bob",
      "motion-adaptive"   : "motion_adaptive",
    },
    "i965" : {
      "bob"               : "bob",
      "motion-adaptive"   : "motion_adaptive",
      "motion-compensated": "motion_compensated",
    },
  }.get(get_media()._get_driver_name(), {}).get(method, None)

@memoize
def map_transpose_direction(degrees, method):
  return {
    (  0,   "vertical") : "vflip",
    (  0, "horizontal") : "hflip",
    ( 90,         None) : "clock",
    ( 90,   "vertical") : "clock_flip",
    ( 90, "horizontal") : "cclock_flip",
    (180,         None) : "reversal",
    (180,   "vertical") : "hflip",
    (180, "horizontal") : "vflip",
    (270,         None) : "cclock",
    (270,   "vertical") : "cclock_flip",
    (270, "horizontal") : "clock_flip",
  }.get( (degrees, method), None)

@memoize
def mapprofile(codec, profile):
  return {
    Codec.AVC   : {
      "high"                  : "high",
      "main"                  : "main",
      "constrained-baseline"  : "constrained_baseline",
    },
    Codec.HEVC  : {
      "main"                  : "main",
      "main444"               : "rext",
      "scc"                   : "scc",
      "scc-444"               : "scc",
      "main10"                : "main10",
      "main444-10"            : "rext",
      "main12"                : "rext",
      "main422-12"            : "rext",
    },
    Codec.JPEG  : {
      "baseline"              : "baseline",
    },
    Codec.MPEG2 : {
      "main"                  : 4,
      "simple"                : 5,
    },
    Codec.VP8   : {
      "version0_3"            : "version0_3",
    },
    Codec.VP9   : {
      "profile0"              : "profile0",
      "profile1"              : "profile1",
      "profile2"              : "profile2",
      "profile3"              : "profile3",
    },
    Codec.AV1   : {
      "main"                  : "main",
      "profile0"              : "main",
    },
  }.get(codec, {}).get(profile, None)

def load_test_spec(*ctx):
  from ....lib import util as libutil
  return libutil.load_test_spec("ffmpeg-vaapi", *ctx)
