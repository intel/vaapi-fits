###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .vpp import VppTest

spec = load_test_spec("vpp", "transpose")

class default(VppTest):
  def before(self):
    vars(self).update(
      caps        = platform.get_caps("vpp", "transpose"),
      vpp_element = "transpose",
    )
    super(default, self).before()

  @slash.requires(*platform.have_caps("vpp", "transpose"))
  @slash.parametrize(*gen_vpp_transpose_parameters(spec))
  def test(self, case, degrees, method):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      degrees = degrees,
      method  = method,
      mmethod = map_vpp_transpose(degrees, method),
    )
    self.vpp()

  def check_metrics(self):
    get_media().baseline.check_md5(
      md5 = md5(self.ofile), context = vars(self).get("refctx", []))
