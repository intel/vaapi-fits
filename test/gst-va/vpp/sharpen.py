###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.vpp import VppSharpenTest as VppTest

spec      = load_test_spec("vpp", "sharpen")
spec_r2r  = load_test_spec("vpp", "sharpen", "r2r")

class default(VppTest):
  @slash.parametrize(*gen_vpp_sharpen_parameters(spec))
  def test(self, case, level):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      level   = level,
    )

    if self.width == 1280 and self.height == 720:
      if "i965" == get_media()._get_driver_name():
        slash.add_failure(
          "1280x720 resolution is known to cause GPU HANG with i965 driver")
        return

    self.vpp()

  @slash.parametrize(*gen_vpp_sharpen_parameters(spec_r2r))
  def test_r2r(self, case, level):
    vars(self).update(spec_r2r[case].copy())
    vars(self).update(case = case, level = level)
    vars(self).setdefault("r2r", 5)
    self.vpp()
