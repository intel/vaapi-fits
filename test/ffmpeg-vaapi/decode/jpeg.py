###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.decoder import DecoderTest

spec = load_test_spec("jpeg", "decode")
spec_r2r = load_test_spec("jpeg", "decode", "r2r")

@slash.requires(*platform.have_caps("decode", "jpeg"))
class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 0.99, minu = 0.99, minv = 0.99)
    self.caps   = platform.get_caps("decode", "jpeg")

    # FIXME: WA since ffmpeg e645a1ddb90a863e129108aad9aa7e2d417f3615, scale
    # csc filter in/out range don't match in ffmpeg vaapi jpeg decode and causes
    # wrong csc.  Thus, force the scaler in/out range to be the same when csc is
    # needed.  This ensures the correct output is produced.  Alternative
    # proposal was to use yuvj* formats... however, hwaccel doesn't support them
    # and they may be removed in the future (deprecated).
    self.ffscale_range = "tv"

    super(default, self).before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    self.case = case
    self.decode()

  @slash.parametrize(("case"), sorted(spec_r2r.keys()))
  def test_r2r(self, case):
    vars(self).update(spec_r2r[case].copy())
    vars(self).setdefault("r2r", 5)
    self.case = case
    self.decode()
