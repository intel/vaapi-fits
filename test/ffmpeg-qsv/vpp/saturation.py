###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.qsv.util import *
from ....lib.ffmpeg.qsv.vpp import VppTest

spec      = load_test_spec("vpp", "saturation")
spec_r2r  = load_test_spec("vpp", "saturation", "r2r")

@slash.requires(*platform.have_caps("vpp", "saturation"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "saturation"),
      vpp_op  = "saturation",
    )
    super().before()

  def init(self, tspec, case, level):
    vars(self).update(tspec[case].copy())
    vars(self).update(case = case, level = level)

  @slash.parametrize(*gen_vpp_saturation_parameters(spec))
  def test(self, case, level):
    self.init(spec, case, level)
    self.vpp()

  @slash.parametrize(*gen_vpp_saturation_parameters(spec_r2r))
  def test_r2r(self, case, level):
    self.init(spec_r2r, case, level)
    vars(self).setdefault("r2r", 5)
    self.vpp()
