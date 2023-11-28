###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.vpp import VppCropTest as VppTest

spec = load_test_spec("vpp", "crop")

class default(VppTest):
  def before(self):
    super().before()
    vars(self).update(metric = dict(type = "md5"))

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
