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
      if self.codec in [Codec.AV1]:
        if "ICQ" == self.rcmode:
          return f" qpi={qp}"
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

def codec_test_class(codec, engine, bitdepth, **kwargs):
  # lowpower setting for codecs that support it
  if codec not in [Codec.JPEG, Codec.MPEG2, Codec.AV1, Codec.VP9]:
    kwargs.update(lowpower = engine == "vdenc")

  # caps lookup translation
  capcodec = codec
  if codec in [Codec.HEVC, Codec.VP9, Codec.AV1]:
    capcodec = f"{codec}_{bitdepth}"

  # gst element codec translation
  gstcodec = {
    Codec.AVC   : "h264",
    Codec.HEVC  : "h265",
    Codec.JPEG  : "mjpeg",
  }.get(codec, codec)

  @slash.requires(*have_gst_element(f"msdk{gstcodec}enc"))
  @slash.requires(*have_gst_element(f"msdk{gstcodec}dec"))
  @slash.requires(*platform.have_caps(engine, capcodec))
  class CodecEncoderTest(EncoderTest):
    def before(self):
      super().before()
      vars(self).update(
        caps = platform.get_caps(engine, capcodec),
        codec = codec,
        gstencoder = f"msdk{gstcodec}enc",
        gstdecoder = f"msdk{gstcodec}dec",
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
        Codec.VP9   : "webm",
        Codec.AV1   : "webm",
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

##### AV1 #####
AV1CommonArgs = dict(
  codec         = Codec.AV1,
  gstmediatype  = "video/x-av1",
  gstmuxer      = "matroskamux",
  gstdemuxer    = "matroskademux",
  gstparser     = "av1parse",
)
AV1EncoderTest      = codec_test_class(bitdepth =  8, engine = "encode", **AV1CommonArgs)
AV1EncoderLPTest    = codec_test_class(bitdepth =  8, engine =  "vdenc", **AV1CommonArgs)
AV1_10EncoderTest   = codec_test_class(bitdepth = 10, engine = "encode", **AV1CommonArgs)
AV1_10EncoderLPTest = codec_test_class(bitdepth = 10, engine =  "vdenc", **AV1CommonArgs)

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
