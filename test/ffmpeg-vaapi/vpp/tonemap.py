###
### Copyright (C) 2018-2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.vpp import VppTest

@slash.requires(*platform.have_caps("vpp", "tonemap"))
@slash.requires(*have_ffmpeg_filter("tonemap_vaapi"))
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

spec_hevc     = load_test_spec("vpp", "tonemap", "hevc_10")
spec_hevc_r2r = load_test_spec("vpp", "tonemap", "hevc_10", "r2r")
@slash.requires(*platform.have_caps("decode", "hevc_10"))
@slash.requires(*have_ffmpeg_filter_options("tonemap_vaapi", "format"))
@slash.requires(*have_ffmpeg_decoder("hevc"))
class hevc(TonemapTest):
  def before(self):
    self.ffdecoder = "hevc"
    super().before()

  @slash.requires(*platform.have_caps("vpp", "tonemap", "h2s"))
  @slash.parametrize(*gen_vpp_h2s_parameters(spec_hevc))
  def test_h2s(self, case, csc):
    self.init(spec_hevc, case, "h2s", csc)
    self.vpp()

  @slash.requires(*platform.have_caps("vpp", "tonemap", "h2s"))
  @slash.parametrize(*gen_vpp_h2s_parameters(spec_hevc_r2r))
  def test_h2s_r2r(self, case, csc):
    self.init(spec_hevc_r2r, case, "h2s", csc)
    vars(self).setdefault("r2r", 5)
    self.vpp()
