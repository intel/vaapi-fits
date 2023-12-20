###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib.common import memoize
from ....lib.ffmpeg.util import *
from ....lib.codecs import Codec

def load_test_spec(*ctx):
  from ....lib import util as libutil
  return libutil.load_test_spec("ffmpeg-d3d12", *ctx)

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
