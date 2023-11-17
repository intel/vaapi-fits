###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.vpp import VppTest

spec      = load_test_spec("vpp", "csc")
spec_r2r  = load_test_spec("vpp", "csc", "r2r")

@slash.requires(*platform.have_caps("vpp", "csc"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "csc"),
      vpp_op  = "csc",
    )
    super(default, self).before()

  @slash.parametrize(*gen_vpp_csc_parameters(spec))
  def test(self, case, csc):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case, csc = csc)
    self.vpp()

  @slash.parametrize(*gen_vpp_csc_parameters(spec_r2r))
  def test_r2r(self, case, csc):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case, csc = csc)
    vars(self).setdefault("r2r", 5)
    self.vpp()
    