###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re
import slash

from ....lib.ffmpeg.encoderbase import BaseEncoderTest, Encoder as FFEncoder
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel
from ....lib.ffmpeg.vaapi.util import mapprofile
from ....lib.ffmpeg.vaapi.decoder import Decoder
from ....lib.common import mapRangeInt, get_media

class Encoder(FFEncoder):
  hwaccel = property(lambda s: "vaapi")
  tilecols = property(lambda s: s.ifprop("tilecols", " -tile_cols_log2 {tilecols}"))
  tilerows = property(lambda s: s.ifprop("tilerows", " -tile_rows_log2 {tilerows}"))

  @property
  def qp(self):
    def inner(qp):
      if self.codec in ["vp8", "vp9"]:
        return f" -global_quality {qp}"
      if self.codec in ["mpeg2"]:
        mqp = mapRangeInt(qp, [0, 100], [1, 31])
        return f" -global_quality {mqp}"
      return " -qp {qp}"
    return self.ifprop("qp", inner)

  @property
  def quality(self):
    def inner(quality):
      if self.codec in ["jpeg"]:
        return " -global_quality {quality}"
      return " -compression_level {quality}"
    return self.ifprop("quality", inner)

  @property
  def encparams(self):
    if self.codec not in ["jpeg"]:
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
        "VAEntrypointEncSlice" if "jpeg" != self.codec else "VAEntrypointEncPicture"),
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
    if vars(self).get("gop", 0) <= 1:
        ipbmode = 0 
    elif vars(self).get("bframes", 0) < 1 or (self.codec in ["avc"] and get_media()._get_gpu_gen() <= 12.7 and vars(self).get("lowpower", 0) == 1):
        ipbmode = 1
    else:
        ipbmode = 2     
    ipbmsgs = [
      "Using intra frames only",
      "Using intra and P-frames|[L|l]ow delay|forward-prediction"
      "|not support P-frames, replacing them with B-frames",
      "Using intra, P- and B-frames|[L|l]ow delay|forward-prediction"
      "|not support P-frames, replacing them with B-frames",
    ]
    m = re.search(ipbmsgs[ipbmode], self.output, re.MULTILINE)
    assert m is not None, "Possible incorrect IPB mode used"
