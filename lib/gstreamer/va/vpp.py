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
from ....lib.common import get_media, mapRange, mapRangeWithDefault

@slash.requires(*have_gst_element("va"))
@slash.requires(*have_gst_element("vapostproc"))
class VppTest(BaseVppTest):
  @property
  def hwdevice(self):
    return get_media().render_device.split('/')[-1]

  def before(self):
    super().before()
    #TODO: windows hwdevice > 0 is not test
    vars(self).update(gstvpp = 'vapostproc' if self.hwdevice in ['renderD128' , '0'] else f"va{self.hwdevice}postproc")

  def map_best_hw_format(self, format, hwformats):
    return map_best_hw_format(format, hwformats)

  def map_format(self, format):
    return mapformat(format)

  def map_formatu(self, format):
    return mapformatu(format)

  def gen_vpp_opts(self):
    opts = ""

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
    elif self.vpp_op in ["denoise"]:
      oprange = dict(
        i965 = [0.0, 1.0],
      ).get(get_media()._get_driver_name(), [0.0, 64.0])
      self.mlevel = mapRange(self.level, [0, 100], oprange)
      opts += " {vpp_op}={mlevel}"
    elif self.vpp_op in ["sharpen"]:
      self.mlevel = mapRangeWithDefault(
        self.level, [0.0, 50.0, 100.0], [0.0, 44.0, 64.0]
      )
      opts += " {vpp_op}={mlevel}"
    elif self.vpp_op in ["transpose"]:
      opts += " video-direction={direction}"
    elif self.vpp_op in ["crop"]:
      opts += " disable-passthrough=true"
    elif self.vpp_op in ["composite"]:
      #TODO: windows hwdevice > 0 is not test
      vacompositor = 'vacompositor' if self.hwdevice in ['renderD128' , '0'] else f"va{self.hwdevice}compositor"
      opts += f" ! tee name=source {vacompositor} name=composite"
      for n, comp in enumerate(self.comps):
        opts += (
          " sink_{n}::xpos={x}"
          " sink_{n}::ypos={y}"
          " sink_{n}::alpha={a}"
          "".format(n = n, **comp)
        )

    return opts

  def gen_output_opts(self):
    vpp_crop_filter = " videocrop left={left} right={right} top={top} bottom={bottom} ! "
    vpp_di_filter   = ' vadeinterlace method={mmethod} ! ' if self.hwdevice in ['renderD128' , '0'] else f" va{self.hwdevice}deinterlace"" method={mmethod} ! "
    opts = super().gen_output_opts()
    if self.vpp_op in ["crop"]:
      opts = vpp_crop_filter + opts
    if self.vpp_op in ["deinterlace"]:
      opts = vpp_di_filter + opts
    if self.vpp_op in ["composite"]:
      opts += " source. ! queue ! composite. " * len(self.comps)
    return opts
