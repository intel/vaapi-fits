###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib.common import memoize
from ....lib.ffmpeg.util import *

def load_test_spec(*ctx):
  from ....lib import util as libutil
  return libutil.load_test_spec("ffmpeg-dxva2", *ctx)
