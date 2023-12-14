###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.vpp import VppCropTest as VppTest

spec      = load_test_spec("vpp", "crop")
spec_r2r  = load_test_spec("vpp", "crop", "r2r")

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

  @slash.parametrize(*gen_vpp_crop_parameters(spec_r2r))
  def test_r2r(self, case, left, right, top, bottom):
    vars(self).update(spec_r2r[case].copy())
    vars(self).update(
      bottom      = bottom,
      case        = case,
      crop_height = self.height - top - bottom,
      crop_width  = self.width - left - right,
      left        = left,
      right       = right,
      top         = top,
    )

    vars(self).setdefault("r2r", 5)
    self.vpp()
