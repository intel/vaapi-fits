###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.vpp import VppTest

spec = load_test_spec("vpp", "denoise")

@slash.requires(*platform.have_caps("vpp", "denoise"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "denoise"),
      vpp_op  = "denoise",
    )
    super(default, self).before()

  @slash.parametrize(*gen_vpp_denoise_parameters(spec))
  def test(self, case, level):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      level   = level,
    )
    self.vpp()
