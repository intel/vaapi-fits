###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.vpp import VppContrastTest as VppTest

spec      = load_test_spec("vpp", "contrast")
spec_r2r  = load_test_spec("vpp", "contrast", "r2r")

class default(VppTest):
  def init(self, tspec, case, level):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case    = case,
      level   = level,
    )

  @slash.parametrize(*gen_vpp_contrast_parameters(spec))
  def test(self, case, level):
    self.init(spec, case, level)
    self.vpp()

  @slash.parametrize(*gen_vpp_contrast_parameters(spec_r2r))
  def test_r2r(self, case, level):
    self.init(spec_r2r, case, level)
    vars(self).setdefault("r2r", 5)
    self.vpp()
