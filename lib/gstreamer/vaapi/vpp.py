###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import math
import os
import slash

from ....lib.gstreamer.vppbase import BaseVppTest
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.vaapi.util import map_best_hw_format, mapformat, mapformatu
from ....lib.common import get_media, mapRange, mapRangeWithDefault

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

    procamp = dict(
      brightness  = [  -1.0,   0.0,   1.0],
      contrast    = [   0.0,   1.0,   2.0],
      hue         = [-180.0,   0.0, 180.0],
      saturation  = [   0.0,   1.0,   2.0],
    )

    if self.vpp_op in procamp:
      self.mlevel = mapRangeWithDefault(
        self.level, [0.0, 50.0, 100.0], procamp[self.vpp_op]
      )
      opts += " {vpp_op}={mlevel}"
    elif self.vpp_op in ["denoise"]:
      ilevel = math.floor(mapRange(self.level, [0, 100], [0.0, 64.0]) + 0.5)
      self.mlevel = mapRange(ilevel, [0, 64], [0.0, 1.0])
      opts += " denoise={mlevel}"
    elif self.vpp_op in ["sharpen"]:
      self.mlevel = mapRangeWithDefault(
        self.level, [0.0, 50.0, 100.0], [-1.0, 0.0, 1.0]
      )
      opts += " sharpen={mlevel}"
    elif self.vpp_op in ["deinterlace"]:
      opts += " deinterlace-mode=1 deinterlace-method={mmethod}"
    elif self.vpp_op in ["transpose"]:
      opts += " video-direction={direction}"
    elif self.vpp_op in ["crop"]:
      opts += " crop-left={left} crop-right={right} crop-top={top} crop-bottom={bottom}"
    elif self.vpp_op in ["composite"]:
      opts += " ! tee name=source vaapioverlay name=composite"
      for n, comp in enumerate(self.comps):
        opts += (
          " sink_{n}::xpos={x}"
          " sink_{n}::ypos={y}"
          " sink_{n}::alpha={a}"
          "".format(n = n, **comp)
        )

    return opts

  def gen_output_opts(self):
    opts = super().gen_output_opts()
    if self.vpp_op in ["composite"]:
      opts += " source. ! queue ! composite. " * len(self.comps)
    return opts
