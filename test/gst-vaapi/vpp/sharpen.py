###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.vpp import VppTest

spec = load_test_spec("vpp", "sharpen")

@slash.requires(*platform.have_caps("vpp", "sharpen"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "sharpen"),
      vpp_op  = "sharpen",
    )
    super(default, self).before()

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
