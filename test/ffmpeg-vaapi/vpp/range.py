###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.vpp import VppTest

spec = load_test_spec("vpp", "color", "range")
@slash.requires(*platform.have_caps("vpp", "range"))
@slash.requires(*have_ffmpeg_filter_options("scale_vaapi", "out_range"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "range"),
      vpp_op  = "range",
    )
    super().before()

  @slash.parametrize(*gen_vpp_color_range_parameters(spec))
  def test(self, case, rng):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      rng     = rng,
    )
    self.vpp()
