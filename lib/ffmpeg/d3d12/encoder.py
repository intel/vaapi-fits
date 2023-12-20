###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re
import slash

from ....lib import platform
from ....lib.ffmpeg.encoderbase import BaseEncoderTest, Encoder as FFEncoder
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel, have_ffmpeg_encoder
from ....lib.ffmpeg.d3d12.util import mapprofile
from ....lib.ffmpeg.d3d12.decoder import Decoder
from ....lib.common import mapRangeInt
from ....lib.codecs import Codec
from ....lib.formats import PixelFormat

class Encoder(FFEncoder):
  hwaccel = property(lambda s: "d3d12va")

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

@slash.requires(*have_ffmpeg_hwaccel("d3d12va"))
class EncoderTest(BaseEncoderTest):
  EncoderClass = Encoder
  DecoderClass = Decoder

  def map_profile(self):
    return mapprofile(self.codec, self.profile)

  def validate_caps(self):
    self.ffencoder = self.ffenc
    super().validate_caps()

  def check_output(self):
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
  # caps lookup translation
  capcodec = codec
  if codec in [Codec.HEVC, Codec.VP9, Codec.AV1]:
    capcodec = f"{codec}_{bitdepth}"

  # ffmpeg plugin codec translation
  ffcodec = {
    Codec.AVC   : "h264",
    Codec.JPEG  : "mjpeg",
  }.get(codec, codec)

  @slash.requires(*have_ffmpeg_encoder(f"{ffcodec}_d3d12va"))
  @slash.requires(*platform.have_caps(engine, capcodec))
  class CodecEncoderTest(EncoderTest):
    def before(self):
      super().before()
      vars(self).update(
        caps = platform.get_caps(engine, capcodec),
        codec = codec,
        ffenc = f"{ffcodec}_d3d12va",
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

  return CodecEncoderTest

##### AVC #####
AVCEncoderTest      = codec_test_class(Codec.AVC, "encode", 8)

##### HEVC #####
HEVC8EncoderTest    = codec_test_class(Codec.HEVC, "encode",  8)
HEVC10EncoderTest   = codec_test_class(Codec.HEVC, "encode", 10)

##### AV1 #####
AV1EncoderTest      = codec_test_class(Codec.AV1, "encode",  8)
AV1_10EncoderTest   = codec_test_class(Codec.AV1, "encode", 10)
