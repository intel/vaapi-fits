###
### Copyright (C) 2024 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.vpp import VppTest

spec      = load_test_spec("vpp", "crop")

@slash.requires(*platform.have_caps("vpp", "crop"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "crop"),
      metric  = dict(type = "md5"),
      vpp_op  = "crop",
    )
    super(default, self).before()

  @slash.parametrize(*gen_vpp_crop_parameters(spec))
  def test(self, case, left, right, top, bottom):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bottom      = bottom,
      case        = case,
      crop_height = self.height - top - bottom,
      crop_width  = self.width - left - right,
      left        = left,
      right       = right,
      top         = top,
    )
    self.vpp()
