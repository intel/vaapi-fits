###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.qsv.util import *
from ....lib.ffmpeg.qsv.vpp import VppTest

spec      = load_test_spec("vpp", "hue")
spec_r2r  = load_test_spec("vpp", "hue", "r2r")

@slash.requires(*platform.have_caps("vpp", "hue"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "hue"),
      vpp_op  = "hue",
      NOOP    = 50, # i.e. 0.0 in ffmpeg range
    )
    super(default, self).before()

  def init(self, tspec, case, level):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case    = case,
      level   = level,
      mlevel  = mapRange(level, [0, 100], [-180.0, 180.0]),
    )

  @slash.parametrize(*gen_vpp_hue_parameters(spec))
  def test(self, case, level):
    self.init(spec, case, level)
    self.vpp()

  @slash.parametrize(*gen_vpp_hue_parameters(spec_r2r))
  def test_r2r(self, case, level):
    self.init(spec_r2r, case, level)
    vars(self).setdefault("r2r", 5)
    self.vpp()

  def check_metrics(self):
    psnr = calculate_psnr(
      self.source, self.decoded,
      self.width, self.height,
      self.frames, self.format)

    assert psnr[-3] == 100, "Luma (Y) should not be affected by HUE filter"

    if self.level == self.NOOP:
      get_media()._set_test_details(psnr = psnr, ref_psnr = "noop")
      assert psnr[-2] == 100, "Cb (U) should not be affected at NOOP level"
      assert psnr[-1] == 100, "Cr (V) should not be affected at NOOP level"
    else:
      def compare(k, ref, actual):
        assert ref is not None, "Invalid reference value"
        assert abs(ref[-2] - actual[-2]) <  0.2, "Cb (U) out of baseline range"
        assert abs(ref[-1] - actual[-1]) <  0.2, "Cr (V) out of baseline range"
      get_media().baseline.check_result(
        compare = compare, context = self.refctx, psnr = psnr)
