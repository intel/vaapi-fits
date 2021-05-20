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
from ....lib.common import get_media

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
    if self.vpp_element in ["contrast"]:
      opts += " contrast={mlevel}"
    elif self.vpp_element in ["saturation"]:
      opts += " saturation={mlevel}"
    elif self.vpp_element in ["hue"]:
      opts += " hue={mlevel}"
    elif self.vpp_element in ["brightness"]:
      opts += " brightness={mlevel}"
    elif self.vpp_element in ["denoise"]:
      opts += " denoise={mlevel}"
    elif self.vpp_element in ["sharpen"]:
      opts += " sharpen={mlevel}"
    elif self.vpp_element in ["transpose"]:
      opts += " video-direction={direction}"

    return opts
