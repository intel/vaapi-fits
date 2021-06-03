###
### Copyright (C) 2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.msdk.util import *
from ....lib.gstreamer.msdk.vpp import VppTest

spec = load_test_spec("vpp", "crop")

@slash.requires(*platform.have_caps("vpp", "crop"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps        = platform.get_caps("vpp", "crop"),
      metric      = dict(type = "md5"),
      vpp_op = "crop",
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

  def check_metrics(self):
    check_filesize(
      self.ofile, self.crop_width, self.crop_height, self.frames, self.format)

    params = vars(self).copy()
    params["width"] = self.crop_width
    params["height"] = self.crop_height
    params["decoded"] = self.ofile

    check_metric(**params)
