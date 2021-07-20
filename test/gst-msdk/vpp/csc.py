###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.msdk.util import *
from ....lib.gstreamer.msdk.vpp import VppTest

spec = load_test_spec("vpp", "csc")

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
