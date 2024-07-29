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
      if self.codec in [Codec.MPEG2]:
        mqp = mapRangeInt(qp, [0, 100], [1, 31])
        return f" -q {mqp}"
      return " -q {qp}"
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

    if self.codec in [Codec.AV1]:
      # ffmpeg-vaapi tilecols and tilerows can't be < 1.
      if self.tilecols < 1 or self.tilerows < 1:
        slash.skip_test(
          f"tilecols and tilerows must be > 0"
          f" : got {self.tilecols} and {self.tilerows}"
        )

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
      qvbr = "RC mode: QVBR",
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

def codec_test_class(codec, engine, bitdepth, **kwargs):
  # lowpower setting for codecs that support it
  if codec not in [Codec.JPEG, Codec.MPEG2]:
    kwargs.update(lowpower = 1 if engine == "vdenc" else 0)

  # caps lookup translation
  capcodec = codec
  if codec in [Codec.HEVC, Codec.VP9, Codec.AV1]:
    capcodec = f"{codec}_{bitdepth}"

  # ffmpeg plugin codec translation
  ffcodec = {
    Codec.AVC   : "h264",
    Codec.JPEG  : "mjpeg",
  }.get(codec, codec)

  @slash.requires(*have_ffmpeg_encoder(f"{ffcodec}_vaapi"))
  @slash.requires(*platform.have_caps(engine, capcodec))
  class CodecEncoderTest(EncoderTest):
    def before(self):
      super().before()
      vars(self).update(
        caps = platform.get_caps(engine, capcodec),
        codec = codec,
        ffenc = f"{ffcodec}_vaapi",
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
        Codec.VP8   : "ivf",
        Codec.VP9   : "ivf",
        Codec.AV1   : "ivf",
      }[codec]

    def get_vaapi_profile(self):
      if Codec.AVC == codec:
        return {
          "high"                  : "VAProfileH264High",
          "main"                  : "VAProfileH264Main",
          "constrained-baseline"  : "VAProfileH264ConstrainedBaseline",
        }[self.profile]
      elif Codec.HEVC == codec:
        return {
          "main"                  : "VAProfileHEVCMain",
          "main444"               : "VAProfileHEVCMain444",
          #profile of "hevc-8bit 422" is mapped to main-422-10 based on
          #https://en.wikipedia.org/wiki/High_Efficiency_Video_Coding#Profiles
          "main422"               : "VAProfileHEVCMain422_10",
          "scc"                   : "VAProfileHEVCSccMain",
          "scc-444"               : "VAProfileHEVCSccMain444",
          "main10"                : "VAProfileHEVCMain10",
          "main444-10"            : "VAProfileHEVCMain444_10",
          "main422-10"            : "VAProfileHEVCMain422_10",
          "main12"                : "VAProfileHEVCMain12",
          "main422-12"            : "VAProfileHEVCMain422_12",
        }[self.profile]
      elif Codec.VP8 == codec:
        return "VAProfileVP8Version0_3"
      elif Codec.VP9 == codec:
        pf = PixelFormat(self.format)
        return {
          ("YUV420",  8) : "VAProfileVP9Profile0",
          ("YUV422",  8) : "VAProfileVP9Profile1",
          ("YUV444",  8) : "VAProfileVP9Profile1",
          ("YUV420", 10) : "VAProfileVP9Profile2",
          ("YUV422", 10) : "VAProfileVP9Profile3",
          ("YUV444", 10) : "VAProfileVP9Profile3",
        }[(pf.subsampling, pf.bitdepth)]
      elif Codec.AV1 == codec:
        return "VAProfileAV1Profile0"
      elif Codec.JPEG == codec:
        return "VAProfileJPEGBaseline"
      elif Codec.MPEG2 == codec:
        return "VAProfileMPEG2.*"

  return CodecEncoderTest

##### AVC #####
AVCEncoderTest      = codec_test_class(Codec.AVC, "encode", 8)
AVCEncoderLPTest    = codec_test_class(Codec.AVC,  "vdenc", 8)

##### HEVC #####
HEVC8EncoderTest    = codec_test_class(Codec.HEVC, "encode",  8)
HEVC8EncoderLPTest  = codec_test_class(Codec.HEVC,  "vdenc",  8)
HEVC10EncoderTest   = codec_test_class(Codec.HEVC, "encode", 10)
HEVC10EncoderLPTest = codec_test_class(Codec.HEVC,  "vdenc", 10)
HEVC12EncoderTest   = codec_test_class(Codec.HEVC, "encode", 12)

##### AV1 #####
AV1EncoderTest      = codec_test_class(Codec.AV1, "encode",  8)
AV1EncoderLPTest    = codec_test_class(Codec.AV1,  "vdenc",  8)
AV1_10EncoderTest   = codec_test_class(Codec.AV1, "encode", 10)
AV1_10EncoderLPTest = codec_test_class(Codec.AV1,  "vdenc", 10)

##### VP9 #####
VP9EncoderTest      = codec_test_class(Codec.VP9, "encode",  8)
VP9EncoderLPTest    = codec_test_class(Codec.VP9,  "vdenc",  8)
VP9_10EncoderTest   = codec_test_class(Codec.VP9, "encode", 10)
VP9_10EncoderLPTest = codec_test_class(Codec.VP9,  "vdenc", 10)

##### VP8 #####
VP8EncoderTest      = codec_test_class(Codec.VP8, "encode", 8)

##### JPEG/MJPEG #####
JPEGEncoderTest     = codec_test_class(Codec.JPEG, "vdenc", 8)

##### MPEG2 #####
MPEG2EncoderTest    = codec_test_class(Codec.MPEG2, "encode", 8)
