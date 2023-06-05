###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.vpp import VppTest

spec = load_test_spec("vpp", "overlay")

@slash.requires(*platform.have_caps("vpp", "blend"))
@slash.requires(*have_ffmpeg_filter("overlay_vaapi"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "blend"),
      vpp_op  = "overlay",
    )
    super().before()

  @slash.parametrize(*gen_vpp_overlay_parameters(spec))
  def test(self, case, alpha):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      alpha   = alpha,
    )
    self.vpp()
