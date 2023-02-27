###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.vpp import VppTest

spec = load_test_spec("vpp", "stack")

@slash.requires(*platform.have_caps("vpp", "blend"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "blend"),
      metric  = dict(type = "md5"),
      vpp_op  = "stack",
    )
    super().before()

  @slash.requires(*have_ffmpeg_filter("hstack_vaapi"))
  @slash.parametrize(*gen_vpp_hstack_parameters(spec))
  def test_hstack(self, case, inputs):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      inputs  = inputs,
      stack   = "hstack",
    )
    self.vpp()

  @slash.requires(*have_ffmpeg_filter("vstack_vaapi"))
  @slash.parametrize(*gen_vpp_vstack_parameters(spec))
  def test_vstack(self, case, inputs):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      inputs  = inputs,
      stack   = "vstack",
    )
    self.vpp()

  @slash.requires(*have_ffmpeg_filter("xstack_vaapi"))
  @slash.parametrize(*gen_vpp_xstack_parameters(spec))
  def test_xstack(self, case, rows, cols, tilew, tileh):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      rows    = rows,
      cols    = cols,
      inputs  = rows * cols,
      tilew   = tilew,
      tileh   = tileh,
      stack   = "xstack",
    )
    self.vpp()
