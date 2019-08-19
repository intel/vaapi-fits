###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .vpp import VppTest

spec = load_test_spec("vpp", "denoise")

class default(VppTest):
  def before(self):
    vars(self).update(
      caps        = platform.get_caps("vpp", "denoise"),
      vpp_element = "denoise",
    )
    super(default, self).before()

  @slash.requires(*platform.have_caps("vpp", "denoise"))
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
      assert abs(ref[-2] - actual[-2]) < 0.2, "Cb (U) out of baseline range"
      assert abs(ref[-1] - actual[-1]) < 0.2, "Cr (V) out of baseline range"

    get_media().baseline.check_result(
      compare = compare, context = vars(self).get("refctx", []), psnr = map(lambda v: round(v, 4), psnr))
