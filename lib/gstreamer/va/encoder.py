###
### Copyright (C) 2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.gstreamer.encoderbase import BaseEncoderTest, Encoder as GstEncoder
from ....lib.gstreamer.util import have_gst_element, get_elements
from ....lib.gstreamer.va.util import mapprofile, map_best_hw_format, mapformat
from ....lib.gstreamer.va.decoder import Decoder
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
  def bframes(self):
    def inner(bframes):
      if self.codec in [Codec.AV1]:
        return " gf-group-size={bframes}"
      return f" b-frames={bframes}"
    return self.ifprop("bframes", inner)

  @property
  def qp(self):
    def inner(qp):
      if self.codec in [Codec.MPEG2]:
        mqp = mapRangeInt(qp, [0, 100], [0, 51])
        return f" qpi={mqp} qpp={mqp} qpb={mqp}"
      if self.codec in [Codec.AV1, Codec.VP9]:
        return f" max-qp={qp} min-qp={qp} qp={qp}"
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
  def gstencoder(self):
    #TODO: windows hwdevice >0 is not test
    return (
      f"{super().gstencoder}"
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

    # WA: https://gitlab.freedesktop.org/gstreamer/gstreamer/-/issues/2736
    # Maximize all gst-va plugin elements rank
    self.__rank_before = os.environ.get("GST_PLUGIN_FEATURE_RANK", None)
    ranks = [] if self.__rank_before is None else self.__rank_before.split(',')
    ranks += [f"{e}:MAX" for e in get_elements("va")]
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
  lp = ""
  if codec not in [Codec.JPEG, Codec.MPEG2]:
    kwargs.update(lowpower = engine == "vdenc")
    lp = "lp" if engine == "vdenc" else ""

  # caps lookup translation
  capcodec = codec
  if codec in [Codec.HEVC, Codec.VP9, Codec.AV1]:
    capcodec = f"{codec}_{bitdepth}"

  # gst element codec translation
  gstcodec = {
    Codec.AVC   : "h264",
    Codec.HEVC  : "h265",
  }.get(codec, codec)

  hwdevice = get_media().render_device.split('/')[-1]
  hw = hwdevice if hwdevice not in ['renderD128', '0'] else ""

  @slash.requires(*have_gst_element(f"va{hw}{gstcodec}{lp}enc"))
  @slash.requires(*have_gst_element(f"va{gstcodec}dec"))
  @slash.requires(*platform.have_caps(engine, capcodec))
  class CodecEncoderTest(EncoderTest):
    def before(self):
      super().before()
      vars(self).update(
        caps = platform.get_caps(engine, capcodec),
        codec = codec,
        gstencoder = f"va{hw}{gstcodec}{lp}enc",
        gstdecoder = f"va{gstcodec}dec",
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
