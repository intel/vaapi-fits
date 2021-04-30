###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.vpp import VppTest

spec = load_test_spec("vpp", "sharpen")

@slash.requires(*platform.have_caps("vpp", "sharpen"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps        = platform.get_caps("vpp", "sharpen"),
      vpp_element = "sharpen",
    )
    super(default, self).before()

  @slash.parametrize(*gen_vpp_sharpen_parameters(spec))
  def test(self, case, level):
    vars(self).update(spec[case].copy())
    if get_media()._get_driver_name() == 'iHD':
      mlevel  = mapRange(level, [0, 100], [0.0, 64.0]),
    else:
      mlevel  = mapRange(level, [0, 100], [0.0, 1.0]),
    vars(self).update(
      case    = case,
      level   = level,
      mlevel  = mlevel,
    )

    if self.width == 1280 and self.height == 720:
      if "i965" == get_media()._get_driver_name():
        slash.add_failure(
          "1280x720 resolution is known to cause GPU HANG with i965 driver")
        return

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
      compare = compare, context = self.refctx, psnr = psnr)
