###
### Copyright (C) 2018-2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.msdk.util import *
from ....lib.gstreamer.msdk.vpp import VppTest

@slash.requires(*platform.have_caps("vpp", "tonemap"))
class TonemapTest(VppTest):
  def before(self):
    vars(self).update(
      vpp_op  = "tonemap",
    )
    super().before()

  def init(self, tspec, case, mode, csc):
    vars(self).update(tspec[case].copy())
    vars(self).update(case = case, mode = mode, csc = csc)
    self.caps = platform.get_caps("vpp", "tonemap", mode)

spec_hevc = load_test_spec("vpp", "tonemap", "hevc_10")
@slash.requires(*platform.have_caps("decode", "hevc_10"))
@slash.requires(*have_gst_element("msdkh265dec"))
class hevc(TonemapTest):
  def before(self):
    self.gstdecoder = "tsdemux ! h265parse ! msdkh265dec"
    super().before()

  @slash.requires(*platform.have_caps("vpp", "tonemap", "h2s"))
  @slash.parametrize(*gen_vpp_h2s_parameters(spec_hevc))
  def test_h2s(self, case, csc):
    self.init(spec_hevc, case, "h2s", csc)
    self.vpp()
