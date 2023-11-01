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
from ....lib import platform
from ....lib.codecs import Codec
from ....lib.common import get_media, mapRangeInt
from ....lib.formats import PixelFormat

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

############################
## AVC Encoders           ##
############################

@slash.requires(*have_gst_element("vaapih264enc"))
@slash.requires(*have_gst_element("vaapih264dec"))
class AVCEncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = Codec.AVC,
      gstencoder    = "vaapih264enc",
      gstdecoder    = "vaapih264dec",
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

@slash.requires(*have_gst_element("vaapih265enc"))
@slash.requires(*have_gst_element("vaapih265dec"))
class HEVCEncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = Codec.HEVC,
      gstencoder    = "vaapih265enc",
      gstdecoder    = "vaapih265dec",
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
## VP9 Encoders           ##
############################

@slash.requires(*have_gst_element("vaapivp9enc"))
@slash.requires(*have_gst_element("vaapivp9dec"))
class VP9EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = Codec.VP9,
      gstencoder    = "vaapivp9enc",
      gstdecoder    = "vaapivp9dec",
      gstmediatype  = "video/x-vp9",
      gstparser     = "vp9parse",
      gstmuxer      = "matroskamux",
      gstdemuxer    = "matroskademux",
    )

  def get_file_ext(self):
    return "webm"

@slash.requires(*platform.have_caps("encode", "vp9_8"))
class VP9EncoderTest(VP9EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps = platform.get_caps("encode", "vp9_8"),
      lowpower  = False,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 8
    super().validate_caps()

@slash.requires(*platform.have_caps("vdenc", "vp9_8"))
class VP9EncoderLPTest(VP9EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps = platform.get_caps("vdenc", "vp9_8"),
      lowpower  = True,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 8
    super().validate_caps()

@slash.requires(*platform.have_caps("encode", "vp9_10"))
class VP9_10EncoderTest(VP9EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "vp9_10"),
      lowpower  = False,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 10
    super().validate_caps()

@slash.requires(*platform.have_caps("vdenc", "vp9_10"))
class VP9_10EncoderLPTest(VP9EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "vp9_10"),
      lowpower  = True,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 10
    super().validate_caps()

############################
## VP8 Encoders           ##
############################

@slash.requires(*have_gst_element("vaapivp8enc"))
@slash.requires(*have_gst_element("vaapivp8dec"))
class VP8EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = Codec.VP8,
      gstencoder    = "vaapivp8enc",
      gstdecoder    = "vaapivp8dec",
      gstmediatype  = "video/x-vp8",
      gstmuxer      = "matroskamux",
      gstdemuxer    = "matroskademux",
    )

  def get_file_ext(self):
    return "webm"

@slash.requires(*platform.have_caps("encode", "vp8"))
class VP8EncoderTest(VP8EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "vp8"),
      lowpower  = False,
    )

############################
## MPEG2 Encoders         ##
############################

@slash.requires(*have_gst_element("vaapimpeg2enc"))
@slash.requires(*have_gst_element("vaapimpeg2dec"))
@slash.requires(*platform.have_caps("encode", "mpeg2"))
class MPEG2EncoderTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      caps          = platform.get_caps("encode", "mpeg2"),
      codec         = Codec.MPEG2,
      gstencoder    = "vaapimpeg2enc",
      gstdecoder    = "vaapimpeg2dec",
      gstmediatype  = "video/mpeg,mpegversion=2",
      gstparser     = "mpegvideoparse",
    )

  def get_file_ext(self):
    return "m2v"

############################
## JPEG/MJPEG Encoders    ##
############################

@slash.requires(*have_gst_element("vaapijpegenc"))
@slash.requires(*have_gst_element("vaapijpegdec"))
@slash.requires(*platform.have_caps("vdenc", "jpeg"))
class JPEGEncoderTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      caps          = platform.get_caps("vdenc", "jpeg"),
      codec         = Codec.JPEG,
      gstencoder    = "vaapijpegenc",
      gstdecoder    = "vaapijpegdec",
      gstmediatype  = "image/jpeg",
      gstparser     = "jpegparse",
    )

  def get_file_ext(self):
    return "mjpeg" if self.frames > 1 else "jpg"
