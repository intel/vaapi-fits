###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.gstreamer.encoderbase import BaseEncoderTest, Encoder as GstEncoder
from ....lib.gstreamer.util import have_gst_element, get_elements
from ....lib.gstreamer.vaapi.util import mapprofile, map_best_hw_format, mapformat
from ....lib.gstreamer.vaapi.decoder import Decoder
from ....lib.codecs import Codec
from ....lib.common import get_media, mapRangeInt

class Encoder(GstEncoder):
  @property
  def hwformat(self):
    return map_best_hw_format(super().format, self.props["caps"]["fmts"])

  @property
  def format(self):
    return mapformat(super().format)

  @property
  def rcmode(self):
    if self.codec in [Codec.JPEG]:
      return ""
    return f" rate-control={super().rcmode}"

  @property
  def qp(self):
    def inner(qp):
      if self.codec in [Codec.MPEG2]:
        mqp = mapRangeInt(qp, [0, 100], [2, 62])
        return f" quantizer={mqp}"
      if self.codec in [Codec.VP8, Codec.VP9]:
        return f" yac-qi={qp}"
      return f" init-qp={qp}"
    return self.ifprop("qp", inner)

  @property
  def quality(self):
    def inner(quality):
      if self.codec in [Codec.JPEG]:
        return f" quality={quality}"
      return f" quality-level={quality}"
    return self.ifprop("quality", inner)

  @property
  def minrate(self):
    if super().rcmode in ["vbr"]:
      tp = self.props["minrate"] / self.props["maxrate"]
      return f" target-percentage={int(tp * 100)}"
    return ""

  gop     = property(lambda s: s.ifprop("gop", " keyframe-period={gop}"))
  slices  = property(lambda s: s.ifprop("slices", " num-slices={slices}"))
  bframes = property(lambda s: s.ifprop("bframes", " max-bframes={bframes}"))
  maxrate = property(lambda s: s.ifprop("maxrate", " bitrate={maxrate}"))
  refmode = property(lambda s: s.ifprop("refmode", " ref-pic-mode={refmode}"))
  refs    = property(lambda s: s.ifprop("refs", " refs={refs}"))
  loopshp = property(lambda s: s.ifprop("loopshp", " sharpness-level={loopshp}"))
  looplvl = property(lambda s: s.ifprop("looplvl", " loop-filter-level={looplvl}"))

  @property
  def gstencoder(self):
    return (
      f"{super().gstencoder}"
      f"{self.rcmode}{self.gop}{self.qp}"
      f"{self.quality}{self.slices}{self.bframes}"
      f"{self.minrate}{self.maxrate}{self.refmode}{self.refs}"
      f"{self.lowpower}{self.loopshp}{self.looplvl}"
    )

@slash.requires(*have_gst_element("vaapi"))
class EncoderTest(BaseEncoderTest):
  EncoderClass = Encoder
  DecoderClass = Decoder

  def before(self):
    super().before()
    os.environ["GST_VAAPI_DRM_DEVICE"] = get_media().render_device

    # WA: https://gitlab.freedesktop.org/gstreamer/gstreamer/-/issues/2736
    # Maximize all gst-vaapi plugin elements rank
    self.__rank_before = os.environ.get("GST_PLUGIN_FEATURE_RANK", None)
    ranks = [] if self.__rank_before is None else self.__rank_before.split(',')
    ranks += [f"{e}:MAX" for e in get_elements("vaapi")]
    os.environ["GST_PLUGIN_FEATURE_RANK"] = ','.join(ranks)

  def after(self):
    super().after()
    if None == self.__rank_before:
      del os.environ["GST_PLUGIN_FEATURE_RANK"]
    else:
      os.environ["GST_PLUGIN_FEATURE_RANK"] = self.__rank_before

  def map_profile(self):
    return mapprofile(self.codec, self.profile)
