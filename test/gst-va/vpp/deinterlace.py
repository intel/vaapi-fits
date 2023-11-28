###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.vpp import VppAVCDeinterlaceTest
from ....lib.gstreamer.va.vpp import VppMPEG2DeinterlaceTest

spec_avc      = load_test_spec("vpp", "deinterlace", "avc")
spec_avc_r2r  = load_test_spec("vpp", "deinterlace", "avc", "r2r")

class avc(VppAVCDeinterlaceTest):
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_avc, VppAVCDeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    self.init(spec_avc, case, method, rate)
    self.vpp()

  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_avc_r2r, VppAVCDeinterlaceTest._default_modes_))
  def test_r2r(self, case, method, rate):
    self.init(spec_avc_r2r, case, method, rate)
    vars(self).setdefault("r2r", 5)
    self.vpp()


spec_mpeg2      = load_test_spec("vpp", "deinterlace", "mpeg2")
spec_mpeg2_r2r  = load_test_spec("vpp", "deinterlace", "mpeg2", "r2r")

class mpeg2(VppMPEG2DeinterlaceTest):
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_mpeg2, VppMPEG2DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    self.init(spec_mpeg2, case, method, rate)
    self.vpp()

  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_mpeg2_r2r, VppMPEG2DeinterlaceTest._default_modes_))
  def test_r2r(self, case, method, rate):
    self.init(spec_mpeg2_r2r, case, method, rate)
    vars(self).setdefault("r2r", 5)
    self.vpp()
