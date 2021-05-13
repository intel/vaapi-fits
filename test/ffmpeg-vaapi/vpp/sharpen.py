###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.vpp import VppTest

spec = load_test_spec("vpp", "sharpen")

@slash.requires(*platform.have_caps("vpp", "sharpen"))
@slash.requires(*have_ffmpeg_filter("sharpness_vaapi"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "sharpen"),
      vpp_op  = "sharpen",
    )
    super(default, self).before()

  @slash.parametrize(*gen_vpp_sharpen_parameters(spec))
  def test(self, case, level):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      level   = level,
      mlevel  = mapRangeInt(level, [0, 100], [0, 64]),
    )

    if self.width == 1280 and self.height == 720:
      if get_media()._get_driver_name() == "i965":
        slash.add_failure(
          "1280x720 resolution is known to cause GPU HANG with i965 driver")
        return

    self.vpp()

  def check_metrics(self):
    psnr = calculate_psnr(
      self.source, self.decoded,
      self.width, self.height,
      self.frames, self.format)

    assert psnr[-2] == 100, "Cb(U) should not be affected by SHARPEN filter"
    assert psnr[-1] == 100, "Cr(V) should not be affected by SHARPEN filter"

    def compare(k, ref, actual):
      assert ref is not None, "Invalid reference value"
      assert abs(ref[-3] - actual[-3]) <  0.2, "Luma (Y) out of baseline range"

    get_media().baseline.check_result(
      compare = compare, context = self.refctx, psnr = psnr)
