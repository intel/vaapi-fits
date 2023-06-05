###
### Copyright (C) 2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash

from ....lib.common import get_media, mapRangeInt, mapRangeWithDefault
from ....lib.ffmpeg.qsv.util import using_compatible_driver
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel, have_ffmpeg_filter
from ....lib.ffmpeg.vppbase import BaseVppTest

@slash.requires(*have_ffmpeg_hwaccel("qsv"))
@slash.requires(*have_ffmpeg_filter("vpp_qsv"))
@slash.requires(using_compatible_driver)
class VppTest(BaseVppTest):
  def before(self):
    super().before()
    self.hwaccel = "qsv"
    self.hwdevice = f'qsv,child_device={get_media().render_device}'

  def get_output_formats(self):
    # MSDK does not support I420 and YV12 output formats even though
    # iHD supports it.  Thus, msdkvpp can't output it directly (HW).
    return list(set(super().get_output_formats()) - set(["I420", "YV12"]))

  def gen_vpp_opts(self):
    vpfilter = []
    if self.vpp_op in ["composite"]:
      vpfilter.append("color=black:size={owidth}x{oheight}")
      vpfilter.append("format={ihwformat}|qsv")
      vpfilter.append("hwupload=extra_hw_frames=16")
      for n, comp in enumerate(self.comps):
        vpfilter[-1] += "[out{n}];[0:v]format={ihwformat}|qsv".format(n = n, **vars(self))
        vpfilter.append(
          "hwupload=extra_hw_frames=16[in{n}];"
          "[out{n}][in{n}]overlay_qsv=x={x}:y={y}:alpha={alpha}"
          "".format(n = n, alpha = mapRangeInt(comp["a"], [0., 1.], [0, 255]), **comp)
        )
    elif self.vpp_op in ["stack"]:
      finputs = "[0:v]" * self.inputs
      vpfilter.append(f"{finputs}{self.stack}_qsv=inputs={self.inputs}")
      if self.stack in ["xstack"]:
        vpfilter[-1] += f":grid={self.cols}x{self.rows}:grid_tile_size={self.tilew}x{self.tileh}"
    elif self.vpp_op in ["overlay"]:
      vpfilter.append("[1:v]hwupload=extra_hw_frames=16[v1];")
      vpfilter[-1] += "[0:v][v1]overlay_qsv=alpha={alpha}"
    else:
      procamp = dict(
        brightness  = [-100.0,   0.0, 100.0],
        contrast    = [   0.0,   1.0,  10.0],
        hue         = [-180.0,   0.0, 180.0],
        saturation  = [   0.0,   1.0,  10.0],
      )

      if self.vpp_op in procamp:
        self.mlevel = mapRangeWithDefault(
          self.level, [0.0, 50.0, 100.0], procamp[self.vpp_op])

      if self.vpp_op not in ["csc", "tonemap"]:
        vpfilter.append("format={ihwformat}|qsv")

      if self.vpp_op not in ["tonemap"]:
        vpfilter.append("hwupload=extra_hw_frames=16")

      vpfilter.append(
        dict(
          brightness  = "vpp_qsv=procamp=1:brightness={mlevel}",
          contrast    = "vpp_qsv=procamp=1:contrast={mlevel}",
          hue         = "vpp_qsv=procamp=1:hue={mlevel}",
          saturation  = "vpp_qsv=procamp=1:saturation={mlevel}",
          denoise     = "vpp_qsv=denoise={level}",
          scale       = "vpp_qsv=w={scale_width}:h={scale_height}",
          scale_qsv   = "scale_qsv=w={scale_width}:h={scale_height}",
          sharpen     = "vpp_qsv=detail={level}",
          deinterlace = "vpp_qsv=deinterlace={mmethod}",
          csc         = "vpp_qsv=format={ohwformat}",
          transpose   = "vpp_qsv=transpose={direction}",
          tonemap     = "vpp_qsv=tonemap=1:format={ohwformat}",
        )[self.vpp_op]
      )

    return vpfilter
