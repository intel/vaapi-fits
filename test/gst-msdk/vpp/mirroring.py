###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .vpp import VppTest

spec = load_test_spec("vpp", "mirroring")

class default(VppTest):
  def before(self):
    vars(self).update(
      caps        = platform.get_caps("vpp", "mirroring"),
      vpp_element = "mirroring",
    )
    super(default, self).before()

  @slash.requires(*platform.have_caps("vpp", "mirroring"))
  @slash.parametrize(*gen_vpp_mirroring_parameters(spec))
  def test(self, case, method):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      method  = method,
      mmethod = map_vpp_mirroring(method),
    )
    self.vpp()

  def check_metrics(self):
    get_media().baseline.check_md5(
      md5 = md5(self.ofile), context = vars(self).get("refctx", []))
