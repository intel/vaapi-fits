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
      if self.codec in [Codec.VP8, Codec.VP9, Codec.AV1]:
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
