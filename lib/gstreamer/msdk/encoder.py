###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import math
import os
import slash

from ....lib.gstreamer.encoderbase import BaseEncoderTest, Encoder as GstEncoder
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.msdk.util import using_compatible_driver, mapprofile, map_best_hw_format, mapformat
from ....lib.gstreamer.msdk.decoder import Decoder
from ....lib import platform
from ....lib.codecs import Codec
from ....lib.common import get_media, mapRangeInt
from ....lib.formats import PixelFormat

class Encoder(GstEncoder):
  @property
  def hwformat(self):
    ifmts = self.props["caps"]["fmts"]
    if self.codec not in [Codec.HEVC, Codec.VP9]:
      ifmts = list(set(ifmts) - set(["AYUV"]))
    return map_best_hw_format(super().format, ifmts)

  @property
  def format(self):
    return mapformat(super().format)

  @property
  def rcmode(self):
    if self.codec in [Codec.JPEG]:
      return ""
    return f" rate-control={super().rcmode} hardware=true"

  @property
  def qp(self):
    def inner(qp):
      if self.codec in [Codec.MPEG2]:
        mqp = mapRangeInt(qp, [0, 100], [0, 51])
        return f" qpi={mqp} qpp={mqp} qpb={mqp}"
      return f" qpi={qp} qpp={qp} qpb={qp}"
    return self.ifprop("qp", inner)

  @property
  def quality(self):
    def inner(quality):
      if self.codec in [Codec.JPEG]:
        return f" quality={quality}"
      return f" target-usage={quality}"
    return self.ifprop("quality", inner)

  @property
  def maxrate(self):
    # kbit/sec, int
    if super().rcmode in ["vbr"]:
      return f" max-vbv-bitrate={self.props['maxrate']}"
    return ""

  @property
  def maxframesize(self):
    # kbyte, int
    def inner(maxframesize):
      return f" max-frame-size={math.ceil(maxframesize)}"
    return self.ifprop("maxframesize", inner)

  @property
  def maxframesize_i(self):
    #kbyte, int
    def inner(maxframesize_i):
      return f" max-frame-size-i={math.ceil(maxframesize_i)}"
    return self.ifprop("maxframesize_i", inner)

  @property
  def maxframesize_p(self):
    #kbyte, int
    def inner(maxframesize_p):
      return f" max-frame-size-p={math.ceil(maxframesize_p)}"
    return self.ifprop("maxframesize_p", inner)

  @property
  def intref(self):
    def inner(intref):
      return (
        f" intra-refresh-type={intref['type']}"
        f" intra-refresh-cycle-size={intref['size']}"
        f" intra-refresh-cycle-dist={intref['dist']}"
      )
    return self.ifprop("intref", inner)

  # Max/min qp
  @property
  def rqp(self):
    def inner(rqp):
      return (
        f" min-qp-i={rqp['MinQPI']}"
        f" max-qp-i={rqp['MaxQPI']}"
        f" min-qp-p={rqp['MinQPP']}"
        f" max-qp-p={rqp['MaxQPP']}"
        f" min-qp-b={rqp['MinQPB']}"
        f" max-qp-b={rqp['MaxQPB']}"
      )
    return self.ifprop("rqp", inner)

  gop     = property(lambda s: s.ifprop("gop", " gop-size={gop}"))
  slices  = property(lambda s: s.ifprop("slices", " num-slices={slices}"))
  bframes = property(lambda s: s.ifprop("bframes", " b-frames={bframes}"))
  minrate = property(lambda s: s.ifprop("minrate", " bitrate={minrate}"))
  refmode = property(lambda s: s.ifprop("refmode", " ref-pic-mode={refmode}"))
  refs    = property(lambda s: s.ifprop("refs", " ref-frames={refs}"))
  ladepth = property(lambda s: s.ifprop("ladepth", " rc-lookahead={ladepth}"))
  tilecols = property(lambda s: s.ifprop("tilecols", " num-tile-cols={tilecols}"))
  tilerows = property(lambda s: s.ifprop("tilerows", " num-tile-rows={tilerows}"))
  ldb     = property(lambda s: s.ifprop("ldb", " lowdelay-brc={ldb}"))
  pict    = property(lambda s: s.ifprop("pict", " pic-timing-sei={pict}"))

  @property
  def gstencoder(self):
    return (
      f"{super().gstencoder}"
      f"{self.rcmode}{self.gop}{self.qp}{self.maxframesize}"
      f"{self.quality}{self.slices}{self.tilecols}{self.tilerows}{self.bframes}"
      f"{self.maxrate}{self.minrate}{self.refmode}"
      f"{self.refs}{self.lowpower}{self.ladepth}{self.pict}"
      f"{self.intref}{self.ldb}{self.maxframesize_i}{self.maxframesize_p}"
      f"{self.rqp}"
    )

@slash.requires(*have_gst_element("msdk"))
@slash.requires(using_compatible_driver)
class EncoderTest(BaseEncoderTest):
  EncoderClass = Encoder
  DecoderClass = Decoder

  def before(self):
    super().before()
    os.environ["GST_MSDK_DRM_DEVICE"] = get_media().render_device

  def map_profile(self):
    return mapprofile(self.codec, self.profile)

  def validate_caps(self):
    if self.rcmode in ['cbr','vbr',]:
    # "brframes", if specified, overrides "frames" for bitrate control modes
      self.frames = vars(self).get("brframes", self.frames)
    super().validate_caps()

############################
## AVC Encoders           ##
############################

@slash.requires(*have_gst_element("msdkh264enc"))
@slash.requires(*have_gst_element("msdkh264dec"))
class AVCEncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = Codec.AVC,
      gstencoder    = "msdkh264enc",
      gstdecoder    = "msdkh264dec",
      gstmediatype  = "video/x-h264",
      gstparser     = "h264parse",
    )

  def get_file_ext(self):
    return "h264"

@slash.requires(*platform.have_caps("encode", "avc"))
class AVCEncoderTest(AVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "avc"),
      lowpower  = False,
    )

@slash.requires(*platform.have_caps("vdenc", "avc"))
class AVCEncoderLPTest(AVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "avc"),
      lowpower  = True,
    )

############################
## HEVC Encoders          ##
############################

@slash.requires(*have_gst_element("msdkh265enc"))
@slash.requires(*have_gst_element("msdkh265dec"))
class HEVCEncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = Codec.HEVC,
      gstencoder    = "msdkh265enc",
      gstdecoder    = "msdkh265dec",
      gstmediatype  = "video/x-h265",
      gstparser     = "h265parse",
    )

  def get_file_ext(self):
    return "h265"

@slash.requires(*platform.have_caps("encode", "hevc_8"))
class HEVC8EncoderTest(HEVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_8"),
      lowpower  = False,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 8
    super().validate_caps()

@slash.requires(*platform.have_caps("vdenc", "hevc_8"))
class HEVC8EncoderLPTest(HEVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "hevc_8"),
      lowpower  = True,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 8
    super().validate_caps()

@slash.requires(*platform.have_caps("encode", "hevc_10"))
class HEVC10EncoderTest(HEVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_10"),
      lowpower  = False,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 10
    super().validate_caps()

@slash.requires(*platform.have_caps("vdenc", "hevc_10"))
class HEVC10EncoderLPTest(HEVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "hevc_10"),
      lowpower  = True,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 10
    super().validate_caps()

@slash.requires(*platform.have_caps("encode", "hevc_12"))
class HEVC12EncoderTest(HEVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_12"),
      lowpower  = False,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 12
    super().validate_caps()

############################
## AV1 Encoders           ##
############################

@slash.requires(*have_gst_element("msdkav1enc"))
@slash.requires(*have_gst_element("msdkav1dec"))
class AV1EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = Codec.AV1,
      gstencoder    = "msdkav1enc",
      gstdecoder    = "msdkav1dec",
      gstmediatype  = "video/x-av1",
      gstmuxer      = "matroskamux",
      gstdemuxer    = "matroskademux",
      gstparser     = "av1parse",
    )

  def get_file_ext(self):
    return "webm"

@slash.requires(*platform.have_caps("encode", "av1_8"))
class AV1EncoderTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "av1_8"),
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 8
    super().validate_caps()

@slash.requires(*platform.have_caps("vdenc", "av1_8"))
class AV1EncoderLPTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "av1_8"),
      # NOTE: msdkav1enc does not have lowpower property.
      # msdkav1enc lowpower is hardcoded internally
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 8
    super().validate_caps()

@slash.requires(*platform.have_caps("encode", "av1_10"))
class AV1_10EncoderTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "av1_10"),
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 10
    super().validate_caps()

@slash.requires(*platform.have_caps("vdenc", "av1_10"))
class AV1_10EncoderLPTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "av1_10"),
      # NOTE: msdkav1enc does not have lowpower property.
      # msdkav1enc lowpower is hardcoded internally
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 10
    super().validate_caps()
