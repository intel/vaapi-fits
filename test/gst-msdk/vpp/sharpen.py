###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.msdk.util import *
from ....lib.gstreamer.msdk.vpp import VppTest

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

    if self.width == 1280 and self.height == 720:
      if os.environ.get("LIBVA_DRIVER_NAME", "i965") == "i965":
        slash.add_failure(
          "1280x720 resolution is known to cause GPU HANG with i965 driver")
        return

    vars(self).update(case = case, level = level)
    self.vpp()
