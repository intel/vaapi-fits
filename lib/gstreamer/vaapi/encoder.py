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

def codec_test_class(codec, engine, bitdepth, **kwargs):
  # lowpower setting for codecs that support it
  if codec not in [Codec.JPEG, Codec.MPEG2]:
    kwargs.update(lowpower = engine == "vdenc")

  # caps lookup translation
  capcodec = codec
  if codec in [Codec.HEVC, Codec.VP9]:
    capcodec = f"{codec}_{bitdepth}"

  # gst element codec translation
  gstcodec = {
    Codec.AVC   : "h264",
    Codec.HEVC  : "h265",
  }.get(codec, codec)

  @slash.requires(*have_gst_element(f"vaapi{gstcodec}enc"))
  @slash.requires(*have_gst_element(f"vaapi{gstcodec}dec"))
  @slash.requires(*platform.have_caps(engine, capcodec))
  class CodecEncoderTest(EncoderTest):
    def before(self):
      super().before()
      vars(self).update(
        caps = platform.get_caps(engine, capcodec),
        codec = codec,
        gstencoder = f"vaapi{gstcodec}enc",
        gstdecoder = f"vaapi{gstcodec}dec",
        **kwargs,
      )

    def validate_caps(self):
      assert PixelFormat(self.format).bitdepth == bitdepth
      super().validate_caps()

    def get_file_ext(self):
      return {
        Codec.AVC   : "h264",
        Codec.HEVC  : "h265",
        Codec.JPEG  : "mjpeg" if self.frames > 1 else "jpg",
        Codec.MPEG2 : "m2v",
        Codec.VP8   : "webm",
        Codec.VP9   : "webm",
      }[codec]

  return CodecEncoderTest

##### AVC #####
AVCCommonArgs = dict(
  codec         = Codec.AVC,
  gstmediatype  = "video/x-h264",
  gstparser     = "h264parse",
)
AVCEncoderTest    = codec_test_class(bitdepth = 8, engine = "encode", **AVCCommonArgs)
AVCEncoderLPTest  = codec_test_class(bitdepth = 8, engine =  "vdenc", **AVCCommonArgs)

##### HEVC #####
HEVCCommonArgs = dict(
  codec         = Codec.HEVC,
  gstmediatype  = "video/x-h265",
  gstparser     = "h265parse",
)
HEVC8EncoderTest    = codec_test_class(bitdepth =  8, engine = "encode", **HEVCCommonArgs)
HEVC8EncoderLPTest  = codec_test_class(bitdepth =  8, engine =  "vdenc", **HEVCCommonArgs)
HEVC10EncoderTest   = codec_test_class(bitdepth = 10, engine = "encode", **HEVCCommonArgs)
HEVC10EncoderLPTest = codec_test_class(bitdepth = 10, engine =  "vdenc", **HEVCCommonArgs)
HEVC12EncoderTest   = codec_test_class(bitdepth = 12, engine = "encode", **HEVCCommonArgs)

##### VP9 #####
VP9CommonArgs = dict(
  codec         = Codec.VP9,
  gstmediatype  = "video/x-vp9",
  gstparser     = "vp9parse",
  gstmuxer      = "matroskamux",
  gstdemuxer    = "matroskademux",
)
VP9EncoderTest      = codec_test_class(bitdepth =  8, engine = "encode", **VP9CommonArgs)
VP9EncoderLPTest    = codec_test_class(bitdepth =  8, engine =  "vdenc", **VP9CommonArgs)
VP9_10EncoderTest   = codec_test_class(bitdepth = 10, engine = "encode", **VP9CommonArgs)
VP9_10EncoderLPTest = codec_test_class(bitdepth = 10, engine =  "vdenc", **VP9CommonArgs)

##### VP8 #####
VP8EncoderTest  = codec_test_class(
  codec         = Codec.VP8,
  engine        = "encode",
  bitdepth      = 8,
  gstmediatype  = "video/x-vp8",
  gstmuxer      = "matroskamux",
  gstdemuxer    = "matroskademux",
)

##### JPEG/MJPEG #####
JPEGEncoderTest = codec_test_class(
  codec         = Codec.JPEG,
  engine        = "vdenc",
  bitdepth      = 8,
  gstmediatype  = "image/jpeg",
  gstparser     = "jpegparse",
)

##### MPEG2 #####
MPEG2EncoderTest = codec_test_class(
  codec         = Codec.MPEG2,
  engine        = "encode",
  bitdepth      = 8,
  gstmediatype  = "video/mpeg,mpegversion=2",
  gstparser     = "mpegvideoparse",
)
