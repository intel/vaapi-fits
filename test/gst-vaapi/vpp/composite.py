###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.vpp import VppTest

spec = load_test_spec("vpp", "composite")

@slash.requires(*platform.have_caps("vpp", "blend"))
@slash.requires(*have_gst_element("vaapioverlay"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "blend"),
      metric  = dict(type = "md5"),
      vpp_op  = "composite",
    )
    super().before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case)
    self.vpp()
