###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.vpp import VppTest

spec = load_test_spec("vpp", "transpose")

@slash.requires(*platform.have_caps("vpp", "transpose"))
@slash.requires(*have_ffmpeg_filter("transpose_vaapi"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "transpose"),
      metric  = dict(type = "md5"),
      vpp_op  = "transpose",
    )
    super(default, self).before()

  @slash.parametrize(*gen_vpp_transpose_parameters(spec))
  def test(self, case, degrees, method):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case      = case,
      degrees   = degrees,
      direction = map_transpose_direction(degrees, method),
      method    = method,
    )

    if self.direction is None:
      slash.skip_test(
        "{degrees} {method} direction not supported".format(**vars(self)))

    self.vpp()

  def check_metrics(self):
    check_metric(**vars(self))
