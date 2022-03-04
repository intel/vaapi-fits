###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.gstreamer.vppbase import BaseVppTest
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.msdk.util import using_compatible_driver
from ....lib.gstreamer.msdk.util import map_best_hw_format, mapformat, mapformatu
from ....lib.common import get_media, mapRange, mapRangeWithDefault

@slash.requires(*have_gst_element("msdk"))
@slash.requires(*have_gst_element("msdkvpp"))
@slash.requires(using_compatible_driver)
class VppTest(BaseVppTest):
  def before(self):
    super().before()
    os.environ["GST_MSDK_DRM_DEVICE"] = get_media().render_device
    vars(self).update(gstvpp = "msdkvpp")

  def get_output_formats(self):
    # MSDK does not support I420 output formats even though
    # iHD supports it.  Thus, msdkvpp can't output it directly (HW).
    return list(set(super().get_output_formats()) - set(["I420"]))

  def map_best_hw_format(self, format, hwformats):
    return map_best_hw_format(format, hwformats)

  def map_format(self, format):
    return mapformat(format)

  def map_formatu(self, format):
    return mapformatu(format)

  def gen_vpp_opts(self):
    opts = "hardware=true"

    procamp = dict(
      brightness  = [-100.0,   0.0, 100.0],
      contrast    = [   0.0,   1.0,  10.0],
      hue         = [-180.0,   0.0, 180.0],
      saturation  = [   0.0,   1.0,  10.0],
    )

    if self.vpp_op in procamp:
      self.mlevel = mapRangeWithDefault(
        self.level, [0.0, 50.0, 100.0], procamp[self.vpp_op]
      )
      opts += " {vpp_op}={mlevel}"
    elif self.vpp_op in ["deinterlace"]:
      opts += " deinterlace-mode=1 deinterlace-method={mmethod}"
    elif self.vpp_op in ["denoise"]:
      opts += " denoise={level}"
    elif self.vpp_op in ["sharpen"]:
      opts += " detail={level}"
    elif self.vpp_op in ["transpose"]:
      opts += " video-direction={direction}"
    elif self.vpp_op in ["crop"]:
      opts += " crop-left={left} crop-right={right}"
      opts += " crop-top={top} crop-bottom={bottom}"

    return opts
