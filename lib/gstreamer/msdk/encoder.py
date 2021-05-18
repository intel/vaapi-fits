###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.gstreamer.encoderbase import BaseEncoderTest
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.msdk.util import using_compatible_driver, mapprofile, map_best_hw_format, mapformat, mapformatu
from ....lib.common import get_media

@slash.requires(*have_gst_element("msdk"))
@slash.requires(using_compatible_driver)
class EncoderTest(BaseEncoderTest):
  def before(self):
    super().before()
    os.environ["GST_MSDK_DRM_DEVICE"] = get_media().render_device

  def map_profile(self):
    return mapprofile(self.codec, self.profile)

  def map_best_hw_format(self):
    ifmts = self.caps["fmts"]
    if self.codec not in ["hevc-8", "vp9"]:
      ifmts = list(set(ifmts) - set(["AYUV"]))
    return map_best_hw_format(self.format, ifmts)

  def map_format(self):
    return mapformat(self.format)

  def map_formatu(self):
    return mapformatu(self.format)

  def gen_encoder_opts(self):
    opts = ""
    if self.codec not in ["jpeg",]:
      opts += " rate-control={rcmode}"
      opts += " hardware=true"
    if vars(self).get("gop", None) is not None:
      opts += " gop-size={gop}"
    if vars(self).get("qp", None) is not None:
      if self.codec in ["mpeg2"]:
        opts += " qpi={mqp} qpp={mqp} qpb={mqp}"
      else:
        opts += " qpi={qp} qpp={qp} qpb={qp}"
    if vars(self).get("quality", None) is not None:
      if self.codec in ["jpeg",]:
        opts += " quality={quality}"
      else:
        opts += " target-usage={quality}"
    if vars(self).get("slices", None) is not None:
      opts += " num-slices={slices}"
    if vars(self).get("bframes", None) is not None:
       opts += " b-frames={bframes}"
    if vars(self).get("rcmode") == "vbr":
       opts += " max-vbv-bitrate={maxrate}"
    if vars(self).get("minrate", None) is not None:
       opts += " bitrate={minrate}"
    if vars(self).get("refmode", None) is not None:
       opts += " ref-pic-mode={refmode}"
    if vars(self).get("refs", None) is not None:
      opts += " ref-frames={refs}"
    if vars(self).get("lowpower", None) is not None:
      opts += " low-power="
      opts += "1" if self.lowpower else "0"
    if vars(self).get("ladepth", None) is not None:
      opts += " rc-lookahead={ladepth}"

    return opts
