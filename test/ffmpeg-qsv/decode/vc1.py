###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .decoder import DecoderTest

spec = load_test_spec("vc1", "decode")
spec_r2r = load_test_spec("vc1", "decode", "r2r")

class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 0.99, minu = 0.99, minv = 0.99)
    super(default, self).before()

  def init(self, tspec, case):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      ffdecoder = "vc1_qsv",
      hwformat  = "nv12",
    )

  @platform_tags(VC1_DECODE_PLATFORMS)
  @slash.requires(*have_ffmpeg_decoder("vc1_qsv"))
  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    self.init(spec, case)
    self.decode()

  @platform_tags(VC1_DECODE_PLATFORMS)
  @slash.requires(*have_ffmpeg_decoder("vc1_qsv"))
  @slash.parametrize(("case"), sorted(spec_r2r.keys()))
  def test_r2r(self, case):
    self.init(spec_r2r, case)
    vars(self).setdefault("r2r", 5)
    self.decode()
