###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .vpp import VppTest

spec = load_test_spec("vpp", "sharpen")

class default(VppTest):
  def before(self):
    vars(self).update(
      vpp_element = "sharpen"
    )
    super(default, self).before()

  @slash.parametrize(*gen_vpp_sharpen_parameters(spec))
  @platform_tags(VPP_PLATFORMS)
  def test(self, case, level):
    vars(self).update(spec[case].copy())

    if self.width == 1280 and self.height == 720:
      if os.environ.get("LIBVA_DRIVER_NAME", "i965") == "i965":
        slash.add_failure(
          "1280x720 resolution is known to cause GPU HANG with i965 driver")
        return

    vars(self).update(case = case, level = level)
    self.vpp()

  def check_metrics(self):
    psnr = calculate_psnr(
      self.source, self.ofile,
      self.width, self.height,
      self.frames, self.format)

    assert psnr[-2] == 100, "Cb(U) should not be affected by SHARPEN filter"
    assert psnr[-1] == 100, "Cr(V) should not be affected by SHARPEN filter"

    def compare(k, ref, actual):
      assert ref is not None, "Invalid reference value"
      assert abs(ref[-3] - actual[-3]) <  0.2, "Luma (Y) out of baseline range"

    get_media().baseline.check_result(
      compare = compare, context = vars(self).get("refctx", []), psnr = map(lambda v: round(v, 4), psnr))
