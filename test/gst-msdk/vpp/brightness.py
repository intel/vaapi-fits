###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .vpp import VppTest

spec = load_test_spec("vpp", "brightness")

class default(VppTest):
  def before(self):
    vars(self).update(
      vpp_element = "brightness",
      NOOP        = 50 # i.e. 0.0 in msdkvpp range should result in no-op result
    )
    super(default, self).before()

  def init(self, tspec, case, level):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      level = level, mlevel = mapRange(level, [0, 100], [-100.0, 100.0]),
      case = case)

  @slash.parametrize(*gen_vpp_brightness_parameters(spec))
  @platform_tags(VPP_PLATFORMS)
  def test(self, case, level):
    self.init(spec, case, level)
    self.vpp()

  def check_metrics(self):
    psnr = calculate_psnr(
      self.source, self.ofile,
      self.width, self.height,
      self.frames, self.format)

    def compare(k, ref, actual):
      assert psnr[-2] == 100, "Cb(U) should not be affected by BRIGHTNESS filter"
      assert psnr[-1] == 100, "Cr(V) should not be affected by BRIGHTNESS filter"
      if self.level == self.NOOP:
        assert psnr[-3] == 100, "Luma (Y) should not be affected at NOOP level"
      else:
        assert ref is not None, "Invalid reference value"
        assert abs(ref[-3] - actual[-3]) <  0.2, "Luma (Y) out of baseline range"

    get_media().baseline.check_result(
      compare = compare, context = vars(self).get("refctx", []), psnr = map(lambda v: round(v, 4), psnr))
