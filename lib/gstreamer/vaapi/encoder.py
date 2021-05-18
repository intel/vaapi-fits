###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.gstreamer.encoderbase import BaseEncoderTest
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.vaapi.util import mapprofile, map_best_hw_format, mapformat, mapformatu
from ....lib.common import get_media

@slash.requires(*have_gst_element("vaapi"))
class EncoderTest(BaseEncoderTest):
  def before(self):
    super().before()
    os.environ["GST_VAAPI_DRM_DEVICE"] = get_media().render_device

  def map_profile(self):
    return mapprofile(self.codec, self.profile)

  def map_best_hw_format(self):
    return map_best_hw_format(self.format, self.caps["fmts"])

  def map_format(self):
    return mapformat(self.format)

  def map_formatu(self):
    return mapformatu(self.format)

  def gen_encoder_opts(self):
    opts = ""
    if self.codec not in ["jpeg",]:
      opts += " rate-control={rcmode}"
    if vars(self).get("gop", None) is not None:
      opts += " keyframe-period={gop}"
    if vars(self).get("qp", None) is not None:
      if self.codec in ["vp8", "vp9",]:
        opts += " yac-qi={qp}"
      elif self.codec in ["mpeg2"]:
        opts += " quantizer={mqp}"
      else:
        opts += " init-qp={qp}"
    if vars(self).get("quality", None) is not None:
      if self.codec in ["jpeg",]:
        opts += " quality={quality}"
      else:
        opts += " quality-level={quality}"
    if vars(self).get("slices", None) is not None:
      opts += " num-slices={slices}"
    if vars(self).get("bframes", None) is not None:
      opts += " max-bframes={bframes}"
    if vars(self).get("maxrate", None) is not None:
      opts += " bitrate={maxrate}"
    if vars(self).get("refmode", None) is not None:
      opts += " ref-pic-mode={refmode}"
    if vars(self).get("refs", None) is not None:
      opts += " refs={refs}"
    if vars(self).get("lowpower", None) is not None:
      opts += " tune="
      opts += "low-power" if self.lowpower else "none"
    if vars(self).get("loopshp", None) is not None:
      opts += " sharpness-level={loopshp}"
    if vars(self).get("looplvl", None) is not None:
      opts += " loop-filter-level={looplvl}"

    return opts
