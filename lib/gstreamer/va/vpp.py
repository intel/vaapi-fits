###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.gstreamer.vppbase import BaseVppTest
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.va.util import map_best_hw_format, mapformat, mapformatu
from ....lib.common import get_media, mapRange

@slash.requires(*have_gst_element("va"))
@slash.requires(*have_gst_element("vapostproc"))
class VppTest(BaseVppTest):
  def before(self):
    super().before()
    # TODO: need gst-va to fix target render device
    vars(self).update(gstvpp = "vapostproc")

  def map_best_hw_format(self, format, hwformats):
    return map_best_hw_format(format, hwformats)

  def map_format(self, format):
    return mapformat(format)

  def map_formatu(self, format):
    return mapformatu(format)

  def gen_vpp_opts(self):
    opts = ""

    procamp = dict(
      brightness  = [-100.0, 100.0],
      contrast    = [   0.0,  10.0],
      hue         = [-180.0, 180.0],
      saturation  = [   0.0,  10.0],
    )

    if self.vpp_op in procamp:
      self.mlevel = mapRange(self.level, [0, 100], procamp[self.vpp_op])
      opts += " {vpp_op}={mlevel}"
    elif self.vpp_op in ["denoise", "sharpen"]:
      oprange = dict(
        i965 = [0.0, 1.0],
      ).get(get_media()._get_driver_name(), [0.0, 64.0])
      self.mlevel = mapRange(self.level, [0, 100], oprange)
      opts += " {vpp_op}={mlevel}"
    elif self.vpp_op in ["transpose"]:
      opts += " video-direction={direction}"

    return opts
