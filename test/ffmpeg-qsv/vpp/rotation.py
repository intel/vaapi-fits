###
### Copyright (C) 2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .vpp import VppTest

spec = load_test_spec("vpp", "rotation")

class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "rotation"),
      metric  = dict(type = "md5"),
      vpp_op  = "transpose",
    )
    super(default, self).before()

  @slash.requires(*platform.have_caps("vpp", "rotation"))
  @slash.parametrize(*gen_vpp_rotation_parameters(spec))
  def test(self, case, degrees):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case      = case,
      degrees   = degrees,
      direction = map_transpose_direction(degrees, None),
      method    = None,
    )

    if self.direction is None:
      slash.skip_test(
        "{degrees} rotation unsupported".format(**vars(self)))

    self.vpp()

  def check_metrics(self):
    check_metric(**vars(self))
