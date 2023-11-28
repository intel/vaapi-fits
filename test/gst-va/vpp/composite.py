###
### Copyright (C) 2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.vpp import VppCompositeTest as VppTest

spec = load_test_spec("vpp", "composite")

class default(VppTest):
  def before(self):
    super().before()
    vars(self).update(metric = dict(type = "md5"))

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case)
    self.vpp()
