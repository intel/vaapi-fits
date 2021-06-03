###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.msdk.util import *
from ....lib.gstreamer.msdk.vpp import VppTest

spec = load_test_spec("vpp", "denoise")

@slash.requires(*platform.have_caps("vpp", "denoise"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps        = platform.get_caps("vpp", "denoise"),
      vpp_op = "denoise",
    )
    super(default, self).before()

  @slash.parametrize(*gen_vpp_denoise_parameters(spec))
  def test(self, case, level):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case, level = level)
    self.vpp()

  def check_metrics(self):
    psnr = calculate_psnr(
      self.source, self.ofile,
      self.width, self.height,
      self.frames, self.format)

    def compare(k, ref, actual):
      assert ref is not None, "Invalid reference value"
      assert abs(ref[-3] - actual[-3]) < 0.2, "Luma (Y) out of baseline range"
      if self.caps.get("chroma", True):
        assert abs(ref[-2] - actual[-2]) < 0.2, "Cb (U) out of baseline range"
        assert abs(ref[-1] - actual[-1]) < 0.2, "Cr (V) out of baseline range"
      else:
        assert actual[-2] == 100, "Cb(U) changed, but caps don't support DENOISE chroma"
        assert actual[-1] == 100, "Cr(V) changed, but caps don't support DENOISE chroma"

    get_media().baseline.check_result(
      compare = compare, context = self.refctx, psnr = psnr)
