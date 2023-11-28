###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.vpp import VppCscTest as VppTest

spec      = load_test_spec("vpp", "csc")
spec_r2r  = load_test_spec("vpp", "csc", "r2r")

class default(VppTest):
  @slash.parametrize(*gen_vpp_csc_parameters(spec))
  def test(self, case, csc):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case, csc = csc)
    self.vpp()

  @slash.parametrize(*gen_vpp_csc_parameters(spec_r2r))
  def test_r2r(self, case, csc):
    vars(self).update(spec_r2r[case].copy())
    vars(self).update(case = case, csc = csc)
    vars(self).setdefault("r2r", 5)
    self.vpp()
