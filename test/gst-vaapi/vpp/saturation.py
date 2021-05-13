###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.vpp import VppTest

spec      = load_test_spec("vpp", "saturation")
spec_r2r  = load_test_spec("vpp", "saturation", "r2r")

@slash.requires(*platform.have_caps("vpp", "saturation"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps        = platform.get_caps("vpp", "saturation"),
      vpp_element = "saturation",
    )
    super(default, self).before()

  def init(self, tspec, case, level):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case    = case,
      level   = level,
      mlevel  = mapRange(level, [0, 100], [0.0, 2.0]),
    )

  @slash.parametrize(*gen_vpp_saturation_parameters(spec))
  def test(self, case, level):
    self.init(spec, case, level)
    self.vpp()

  @slash.parametrize(*gen_vpp_saturation_parameters(spec_r2r))
  def test_r2r(self, case, level):
    self.init(spec_r2r, case, level)
    vars(self).setdefault("r2r", 5)
    self.vpp()

  def check_metrics(self):
    psnr = calculate_psnr(
      self.source, self.ofile,
      self.width, self.height,
      self.frames, self.format)

    assert psnr[-3] == 100, "Luma (Y) should not be affected by SATURATION filter"

    def compare(k, ref, actual):
      assert ref is not None, "Invalid reference value"
      assert abs(ref[-2] - actual[-2]) <  0.2, "Cb (U) out of baseline range"
      assert abs(ref[-1] - actual[-1]) <  0.2, "Cr (V) out of baseline range"

    get_media().baseline.check_result(
      compare = compare, context = self.refctx, psnr = psnr)
