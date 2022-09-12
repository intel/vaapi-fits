###
### Copyright (C) 2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.vpp import VppTest

spec = load_test_spec("vpp", "mirroring")

@slash.requires(*platform.have_caps("vpp", "mirroring"))
@slash.requires(*have_ffmpeg_filter("transpose_vaapi"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "mirroring"),
      metric  = dict(type = "md5"),
      vpp_op  = "transpose",
    )
    super().before()

  @slash.parametrize(*gen_vpp_mirroring_parameters(spec))
  def test(self, case, method):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case      = case,
      degrees   = 0,
      direction = map_transpose_direction(0, method),
      method    = method,
    )

    if self.direction is None:
      slash.skip_test(f"{method} mirroring unsupported")

    self.vpp()
