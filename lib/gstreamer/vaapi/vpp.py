###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.gstreamer.vppbase import BaseVppTest
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.vaapi.util import map_best_hw_format, mapformat, mapformatu
from ....lib.common import get_media

@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapipostproc"))
class VppTest(BaseVppTest):
  def before(self):
    super().before()
    os.environ["GST_VAAPI_DRM_DEVICE"] = get_media().render_device
    vars(self).update(gstvpp = "vaapipostproc")

  def map_best_hw_format(self, format, hwformats):
    return map_best_hw_format(format, hwformats)

  def map_format(self, format):
    return mapformat(format)

  def map_formatu(self, format):
    return mapformatu(format)

  def gen_vpp_opts(self):
    opts = ""
    if self.vpp_op in ["contrast"]:
      opts += " contrast={mlevel}"
    elif self.vpp_op in ["saturation"]:
      opts += " saturation={mlevel}"
    elif self.vpp_op in ["hue"]:
      opts += " hue={mlevel}"
    elif self.vpp_op in ["brightness"]:
      opts += " brightness={mlevel}"
    elif self.vpp_op in ["denoise"]:
      opts += " denoise={mlevel}"
    elif self.vpp_op in ["sharpen"]:
      opts += " sharpen={mlevel}"
    elif self.vpp_op in ["deinterlace"]:
      opts += " deinterlace-mode=1 deinterlace-method={mmethod}"
    elif self.vpp_op in ["transpose"]:
      opts += " video-direction={direction}"
    elif self.vpp_op in ["crop"]:
      opts += " crop-left={left} crop-right={right} crop-top={top} crop-bottom={bottom}"

    return opts
