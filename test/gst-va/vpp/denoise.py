###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.vpp import VppDenoiseTest as VppTest

spec      = load_test_spec("vpp", "denoise")
spec_r2r  = load_test_spec("vpp", "denoise", "r2r")

class default(VppTest):
  @slash.parametrize(*gen_vpp_denoise_parameters(spec))
  def test(self, case, level):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      level   = level,
    )
    self.vpp()

  @slash.parametrize(*gen_vpp_denoise_parameters(spec_r2r))
  def test_r2r(self, case, level):
    vars(self).update(spec_r2r[case].copy())
    vars(self).update(case = case, level = level)
    vars(self).setdefault("r2r", 5)
    self.vpp()
