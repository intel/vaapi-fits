###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re
import slash

from ....lib import platform
from ....lib.ffmpeg.encoderbase import BaseEncoderTest, Encoder as FFEncoder
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel, have_ffmpeg_encoder
from ....lib.ffmpeg.vaapi.util import mapprofile
from ....lib.ffmpeg.vaapi.decoder import Decoder
from ....lib.common import mapRangeInt
from ....lib.codecs import Codec
from ....lib.formats import PixelFormat

class Encoder(FFEncoder):
  hwaccel = property(lambda s: "vaapi")

  # connect tile cols/rows into "-tiles", and leave tilerows empty.
  tilecols = property(lambda s: s.ifprop("tilecols", " -tiles {tilecols}x{tilerows}"))
  tilerows = property(lambda s: s.ifprop("tilerows", ""))

  @property
  def profile(self):
    if self.codec in [Codec.VP8]:
      return ""
    return super().profile

  @property
  def qp(self):
    def inner(qp):
      if self.codec in [Codec.VP8, Codec.VP9]:
        return f" -global_quality {qp}"
      if self.codec in [Codec.AV1]:
        if "ICQ" == self.rcmode:
          return f" -global_quality {qp}"
      if self.codec in [Codec.MPEG2]:
        mqp = mapRangeInt(qp, [0, 100], [1, 31])
        return f" -global_quality {mqp}"
      return " -qp {qp}"
    return self.ifprop("qp", inner)

  @property
  def quality(self):
    def inner(quality):
      if self.codec in [Codec.JPEG]:
        return " -global_quality {quality}"
      return " -compression_level {quality}"
    return self.ifprop("quality", inner)

  @property
  def encparams(self):
    if self.codec not in [Codec.JPEG]:
      return f"-rc_mode {self.rcmode}{super().encparams}"
    return super().encparams

@slash.requires(*have_ffmpeg_hwaccel("vaapi"))
class EncoderTest(BaseEncoderTest):
  EncoderClass = Encoder
  DecoderClass = Decoder

  def get_vaapi_profile(self):
    raise NotImplementedError

  def map_profile(self):
    return mapprofile(self.codec, self.profile)

  def validate_caps(self):
    self.ffencoder = self.ffenc
    super().validate_caps()

  def check_output(self):
    # profile
    m = re.search(
      "Using VAAPI profile {} ([0-9]*)".format(self.get_vaapi_profile()),
      self.output, re.MULTILINE)
    assert m is not None, "Possible incorrect profile used"

    # entrypoint
    entrypointmsgs = [
      "Using VAAPI entrypoint {} ([0-9]*)".format(
        "VAEntrypointEncSlice" if Codec.JPEG != self.codec else "VAEntrypointEncPicture"),
      "Using VAAPI entrypoint VAEntrypointEncSliceLP ([0-9]*)",
    ]
    m = re.search(
      entrypointmsgs[vars(self).get("lowpower", 0)], self.output, re.MULTILINE)
    assert m is not None, "Possible incorrect entrypoint used"

    # rate control mode
    rcmsgs = dict(
      cqp = (
        "Using constant-quality mode"
        "|RC mode: CQP"
        "|Driver does not report any supported rate control modes: assuming constant-quality"
      ),
      icq = "RC mode: ICQ",
      cbr = "RC mode: CBR",
      vbr = "RC mode: VBR",
    )
    m = re.search(rcmsgs[self.rcmode], self.output, re.MULTILINE)
    assert m is not None, "Possible incorrect RC mode used"

    # ipb mode
    ipbmode = 0 if vars(self).get("gop", 0) <= 1 else 1 if vars(self).get("bframes", 0) < 1 else 2
    ipbmsgs = [
      "Using intra frames only",
      "Using intra and P-frames|[L|l]ow delay|forward-prediction"
      "|not support P-frames, replacing them with B-frames",
      "Using intra, P- and B-frames|[L|l]ow delay|forward-prediction"
      "|not support P-frames, replacing them with B-frames",
    ]
    m = re.search(ipbmsgs[ipbmode], self.output, re.MULTILINE)
    assert m is not None, "Possible incorrect IPB mode used"

############################
## VP8 Encoders           ##
############################

@slash.requires(*have_ffmpeg_encoder("vp8_vaapi"))
@slash.requires(*platform.have_caps("encode", "vp8"))
class VP8EncoderTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec     = Codec.VP8,
      ffenc     = "vp8_vaapi",
      caps      = platform.get_caps("encode", "vp8"),
      lowpower  = 0,
    )

  def get_file_ext(self):
    return "ivf"

  def get_vaapi_profile(self):
    return "VAProfileVP8Version0_3"

############################
## AVC Encoders           ##
############################

@slash.requires(*have_ffmpeg_encoder("h264_vaapi"))
class AVCEncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec   = Codec.AVC,
      ffenc   = "h264_vaapi",
    )

  def get_file_ext(self):
    return "h264"

  def get_vaapi_profile(self):
    return {
      "high"                  : "VAProfileH264High",
      "main"                  : "VAProfileH264Main",
      "constrained-baseline"  : "VAProfileH264ConstrainedBaseline",
    }[self.profile]

@slash.requires(*platform.have_caps("encode", "avc"))
class AVCEncoderTest(AVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "avc"),
      lowpower  = 0,
    )

@slash.requires(*platform.have_caps("vdenc", "avc"))
class AVCEncoderLPTest(AVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "avc"),
      lowpower  = 1,
    )

############################
## HEVC Encoders          ##
############################

@slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
class HEVCEncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec   = Codec.HEVC,
      ffenc   = "hevc_vaapi",
    )

  def get_file_ext(self):
    return "h265"

  def get_vaapi_profile(self):
    return {
      "main"        : "VAProfileHEVCMain",
      "main444"     : "VAProfileHEVCMain444",
      "scc"         : "VAProfileHEVCSccMain",
      "scc-444"     : "VAProfileHEVCSccMain444",
      "main10"      : "VAProfileHEVCMain10",
      "main444-10"  : "VAProfileHEVCMain444_10",
      "main12"      : "VAProfileHEVCMain12",
      "main422-12"  : "VAProfileHEVCMain422_12",
    }[self.profile]

@slash.requires(*platform.have_caps("encode", "hevc_8"))
class HEVC8EncoderTest(HEVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_8"),
      lowpower  = 0,
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
      lowpower  = 1,
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
      lowpower  = 0,
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
      lowpower  = 1,
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
      lowpower  = 0,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 12
    super().validate_caps()

############################
## VP9 Encoders           ##
############################

@slash.requires(*have_ffmpeg_encoder("vp9_vaapi"))
class VP9EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec   = Codec.VP9,
      ffenc   = "vp9_vaapi",
    )

  def get_file_ext(self):
    return "ivf"

  def get_vaapi_profile(self):
    pf = PixelFormat(self.format)
    return {
      ("YUV420",  8) : "VAProfileVP9Profile0",
      ("YUV422",  8) : "VAProfileVP9Profile1",
      ("YUV444",  8) : "VAProfileVP9Profile1",
      ("YUV420", 10) : "VAProfileVP9Profile2",
      ("YUV422", 10) : "VAProfileVP9Profile3",
      ("YUV444", 10) : "VAProfileVP9Profile3",
    }[(pf.subsampling, pf.bitdepth)]

@slash.requires(*platform.have_caps("encode", "vp9_8"))
class VP9EncoderTest(VP9EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "vp9_8"),
      lowpower  = 0,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 8
    super().validate_caps()

@slash.requires(*platform.have_caps("vdenc", "vp9_8"))
class VP9EncoderLPTest(VP9EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "vp9_8"),
      lowpower  = 1,
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
      lowpower  = 0,
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
      lowpower  = 1,
    )

  def validate_caps(self):
    assert PixelFormat(self.format).bitdepth == 10
    super().validate_caps()
