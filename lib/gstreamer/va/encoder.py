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

############################
## AVC Encoders           ##
############################

@slash.requires(*have_gst_element("vah264dec"))
class AVCEncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = Codec.AVC,
      gstdecoder    = "vah264dec",
      gstmediatype  = "video/x-h264",
      gstparser     = "h264parse",
    )

  def get_file_ext(self):
    return "h264"

@slash.requires(*have_gst_element("vah264enc"))
@slash.requires(*platform.have_caps("encode", "avc"))
class AVCEncoderTest(AVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "avc"),
      gstencoder= "vah264enc",
      lowpower  = False,
    )

@slash.requires(*have_gst_element("vah264lpenc"))
@slash.requires(*platform.have_caps("vdenc", "avc"))
class AVCEncoderLPTest(AVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "avc"),
      gstencoder= "vah264lpenc",
      lowpower  = True,
    )

############################
## HEVC Encoders          ##
############################

@slash.requires(*have_gst_element("vah265dec"))
class HEVCEncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = Codec.HEVC,
      gstdecoder    = "vah265dec",
      gstmediatype  = "video/x-h265",
      gstparser     = "h265parse",
    )

  def get_file_ext(self):
    return "h265"

@slash.requires(*have_gst_element("vah265enc"))
@slash.requires(*platform.have_caps("encode", "hevc_8"))
class HEVC8EncoderTest(HEVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_8"),
      gstencoder= "vah265enc",
      lowpower  = False,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 8
    super().validate_caps()

@slash.requires(*have_gst_element("vah265lpenc"))
@slash.requires(*platform.have_caps("vdenc", "hevc_8"))
class HEVC8EncoderLPTest(HEVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "hevc_8"),
      gstencoder= "vah265lpenc",
      lowpower  = True,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 8
    super().validate_caps()

@slash.requires(*have_gst_element("vah265enc"))
@slash.requires(*platform.have_caps("encode", "hevc_10"))
class HEVC10EncoderTest(HEVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_10"),
      gstencoder= "vah265enc",
      lowpower  = False,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 10
    super().validate_caps()

@slash.requires(*have_gst_element("vah265lpenc"))
@slash.requires(*platform.have_caps("vdenc", "hevc_10"))
class HEVC10EncoderLPTest(HEVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "hevc_10"),
      gstencoder= "vah265lpenc",
      lowpower  = True,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 10
    super().validate_caps()

@slash.requires(*have_gst_element("vah265enc"))
@slash.requires(*platform.have_caps("encode", "hevc_12"))
class HEVC12EncoderTest(HEVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_12"),
      gstencoder= "vah265enc",
      lowpower  = False,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 12
    super().validate_caps()

############################
## AV1 Encoders           ##
############################

@slash.requires(*have_gst_element("vaav1dec"))
class AV1EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = Codec.AV1,
      gstdecoder    = "vaav1dec",
      gstmediatype  = "video/x-av1",
      gstmuxer      = "matroskamux",
      gstdemuxer    = "matroskademux",
      gstparser     = "av1parse",
    )

  def get_file_ext(self):
    return "webm"

@slash.requires(*have_gst_element("vaav1enc"))
@slash.requires(*platform.have_caps("encode", "av1_8"))
class AV1EncoderTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "av1_8"),
      gstencoder= "vaav1enc",
      lowpower  = False,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 8
    super().validate_caps()

@slash.requires(*have_gst_element("vaav1lpenc"))
@slash.requires(*platform.have_caps("vdenc", "av1_8"))
class AV1EncoderLPTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "av1_8"),
      gstencoder= "vaav1lpenc",
      lowpower  = True,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 8
    super().validate_caps()

@slash.requires(*have_gst_element("vaav1enc"))
@slash.requires(*platform.have_caps("encode", "av1_10"))
class AV1_10EncoderTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps        = platform.get_caps("encode", "av1_10"),
      gstencoder  = "vaav1enc",
      lowpower    = False,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 10
    super().validate_caps()

@slash.requires(*have_gst_element("vaav1lpenc"))
@slash.requires(*platform.have_caps("vdenc", "av1_10"))
class AV1_10EncoderLPTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps        = platform.get_caps("vdenc", "av1_10"),
      gstencoder  = "vaav1lpenc",
      lowpower    = True,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 10
    super().validate_caps()
