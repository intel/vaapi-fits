###
### Copyright (C) 2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.gstreamer.encoderbase import BaseEncoderTest, Encoder as GstEncoder
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.va.util import mapprofile, map_best_hw_format, mapformat
from ....lib.gstreamer.va.decoder import Decoder
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
    if self.codec in ["jpeg"]:
      return ""
    return f" rate-control={super().rcmode}"

  @property
  def bframes(self):
    def inner(bframes):
      if self.codec in ["av1-8"]:
        return " gf-group-size={bframes}"
      return f" b-frames={bframes}"
    return self.ifprop("bframes", inner)

  @property
  def qp(self):
    def inner(qp):
      if self.codec in ["mpeg2"]:
        mqp = mapRangeInt(qp, [0, 100], [0, 51])
        return f" qpi={mqp} qpp={mqp} qpb={mqp}"
      if self.codec in ["vp8", "vp9"]:
        return f" qpi={qp}"
      if self.codec in ["av1-8"]:
        return f" max-qp={qp} min-qp={qp} qp={qp}"
      return f" qpi={qp} qpp={qp} qpb={qp}"
    return self.ifprop("qp", inner)

  @property
  def quality(self):
    def inner(quality):
      if self.codec in ["jpeg"]:
        return f" quality={quality}"
      return f" target-usage={quality}"
    return self.ifprop("quality", inner)

  @property
  def maxrate(self):
    ## From gstreamer/subprojects/gst-plugins-bad/sys/va/gstvah264enc.c
    ##
    ## VBR mode: "rate-control=VBR", then the "bitrate" specify the
    ## target bit rate, "target-percentage" is used to calculate the
    ## max bit rate of VBR mode by ("bitrate" * 100) /
    ## "target-percentage".
    ##
    if super().rcmode in ["vbr"]:
      tp = self.props["minrate"] / self.props["maxrate"]
      return f" target-percentage={int(tp * 100)}"
    return ""

  @property # overrides base
  def lowpower(self):
    # gst-va implements lowpower as a separate element instead of using a gst property
    if self.props.get('lowpower', False):
      assert super().gstencoder.endswith("lpenc")
    else:
      assert not super().gstencoder.endswith("lpenc")
    return ""

  gop     = property(lambda s: s.ifprop("gop", " key-int-max={gop}"))
  slices  = property(lambda s: s.ifprop("slices", " num-slices={slices}"))
  minrate = property(lambda s: s.ifprop("minrate", " bitrate={minrate}"))
  refmode = property(lambda s: s.ifprop("refmode", " ref-pic-mode={refmode}"))
  refs    = property(lambda s: s.ifprop("refs", " ref-frames={refs}"))
  loopshp = property(lambda s: s.ifprop("loopshp", " sharpness-level={loopshp}"))
  looplvl = property(lambda s: s.ifprop("looplvl", " loop-filter-level={looplvl}"))
  tilecols = property(lambda s: s.ifprop("tilecols", " num-tile-cols={tilecols}"))
  tilerows = property(lambda s: s.ifprop("tilerows", " num-tile-rows={tilerows}"))

  @property
  def hwdevice(self):
    return get_media().render_device.split('/')[-1]

  @property
  def gstencoder(self):
    #TODO: windows hwdevice >0 is not test
    return (
      f"{super().gstencoder if self.hwdevice in ['renderD128', '0'] else super().gstencoder.replace('va', f'va{self.hwdevice}')}"
      f"{self.rcmode}{self.gop}{self.qp}{self.tilecols}{self.tilerows}"
      f"{self.quality}{self.slices}{self.bframes}"
      f"{self.minrate}{self.maxrate}{self.refmode}{self.refs}"
      f"{self.lowpower}{self.loopshp}{self.looplvl}"
    )

@slash.requires(*have_gst_element("va"))
class EncoderTest(BaseEncoderTest):
  EncoderClass = Encoder
  DecoderClass = Decoder

  def before(self):
    super().before()

  def map_profile(self):
    return mapprofile(self.codec, self.profile)
