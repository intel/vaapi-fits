###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.vpp import VppTransposeTest as VppTest

spec      = load_test_spec("vpp", "transpose")
spec_r2r  = load_test_spec("vpp", "transpose", "r2r")

class default(VppTest):
  def before(self):
    super().before()
    vars(self).update(metric = dict(type = "md5"))

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

  @slash.parametrize(*gen_vpp_transpose_parameters(spec_r2r))
  def test_r2r(self, case, degrees, method):
    vars(self).update(spec_r2r[case].copy())
    vars(self).update(
      case      = case,
      degrees   = degrees,
      direction = map_transpose_direction(degrees, method),
      method    = method,
    )

    if self.direction is None:
      slash.skip_test(
        "{degrees} {method} direction not supported".format(**vars(self)))

    vars(self).setdefault("r2r", 5)
    self.vpp()
