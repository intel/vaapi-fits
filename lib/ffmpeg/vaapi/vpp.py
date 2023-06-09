###
### Copyright (C) 2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from .util import *

import slash

from ....lib.common import get_media, mapRange, mapRangeInt, mapRangeWithDefault
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel
from ....lib.ffmpeg.vppbase import BaseVppTest

@slash.requires(*have_ffmpeg_hwaccel("vaapi"))
class VppTest(BaseVppTest):
  def before(self):
    super().before()
    self.hwaccel = "vaapi"

  def gen_vpp_opts(self):
    vpfilter = []
    if self.vpp_op in ["composite"]:
      vpfilter.append("color=black:size={owidth}x{oheight}")
      vpfilter.append("format={ihwformat}|vaapi")
      vpfilter.append("hwupload")
      for n, comp in enumerate(self.comps):
        vpfilter[-1] += "[out{n}];[0:v]format={ihwformat}|vaapi".format(n = n, **vars(self))
        vpfilter.append(
          "hwupload[in{n}];[out{n}][in{n}]overlay_vaapi=x={x}:y={y}:alpha={a}"
          "".format(n = n, **comp)
        )
    elif self.vpp_op in ["stack"]:
      finputs = "[0:v]" * self.inputs
      vpfilter.append(f"{finputs}{self.stack}_vaapi=inputs={self.inputs}")
      if self.stack in ["xstack"]:
        vpfilter[-1] += f":grid={self.cols}x{self.rows}:grid_tile_size={self.tilew}x{self.tileh}"
    elif self.vpp_op in ["overlay"]:
      vpfilter.append("[1:v]hwupload[v1];")
      vpfilter[-1] += "[0:v][v1]overlay_vaapi=alpha={a}".format(a = mapRange(self.alpha, [0.0, 255.0], [0.0, 1.0]))
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
      elif self.vpp_op in ["denoise"]:
        self.mlevel = mapRange(self.level, [0.0, 100.0], [0.0, 64.0])
      elif self.vpp_op in ["sharpen"]:
        self.mlevel = mapRangeInt(self.level, [0, 100], [0, 64])

      if self.vpp_op not in ["csc", "tonemap", "range"]:
        vpfilter.append("format={ihwformat}|vaapi")

      if self.vpp_op not in ["tonemap", "range"]:
        vpfilter.append("hwupload")

      vpfilter.append(
        dict(
          brightness  = "procamp_vaapi=b={mlevel}",
          contrast    = "procamp_vaapi=c={mlevel}",
          hue         = "procamp_vaapi=h={mlevel}",
          saturation  = "procamp_vaapi=s={mlevel}",
          denoise     = "denoise_vaapi=denoise={mlevel}",
          scale       = "scale_vaapi=w={scale_width}:h={scale_height}",
          sharpen     = "sharpness_vaapi=sharpness={mlevel}",
          deinterlace = "deinterlace_vaapi=mode={mmethod}:rate={rate}",
          csc         = "scale_vaapi=format={ohwformat}",
          transpose   = "transpose_vaapi=dir={direction}",
          tonemap     = "tonemap_vaapi=format={ohwformat}",
          range       = "scale_vaapi=out_range={rng}",
        )[self.vpp_op]
      )

    return vpfilter
