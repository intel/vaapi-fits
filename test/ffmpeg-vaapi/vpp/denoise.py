###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.vpp import VppTest

spec      = load_test_spec("vpp", "denoise")
spec_r2r  = load_test_spec("vpp", "denoise", "r2r")

@slash.requires(*platform.have_caps("vpp", "denoise"))
@slash.requires(*have_ffmpeg_filter("denoise_vaapi"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "denoise"),
      vpp_op  = "denoise",
    )
    super().before()

  @slash.parametrize(*gen_vpp_denoise_parameters(spec))
  def test(self, case, level):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case, level = level)
    self.vpp()

  @slash.parametrize(*gen_vpp_denoise_parameters(spec_r2r))
  def test_r2r(self, case, level):
    vars(self).update(spec_r2r[case].copy())
    vars(self).update(case = case, level = level)
    vars(self).setdefault("r2r", 5)
    self.vpp()
