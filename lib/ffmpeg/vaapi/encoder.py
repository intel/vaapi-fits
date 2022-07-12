###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re
import slash

from ....lib.ffmpeg.encoderbase import BaseEncoderTest
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel
from ....lib.ffmpeg.vaapi.util import mapprofile

@slash.requires(*have_ffmpeg_hwaccel("vaapi"))
class EncoderTest(BaseEncoderTest):
  def before(self):
    super().before()
    self.hwaccel = "vaapi"
    self.hwupload = True
    self.hwdownload = True

  def get_vaapi_profile(self):
    raise NotImplementedError

  def map_profile(self):
    return mapprofile(self.codec, self.profile)

  def gen_qp_opts(self):
    if self.codec in ["vp8", "vp9",]:
      return " -global_quality {qp}"
    if self.codec in ["mpeg2"]:
      return " -global_quality {mqp}"
    return " -qp {qp}"

  def gen_quality_opts(self):
    if self.codec in ["jpeg"]:
      return " -global_quality {quality}"
    return " -compression_level {quality}"

  def validate_caps(self):
    super().validate_caps()
    self.ffencoder = self.ffenc
    if self.codec not in ["jpeg"]:
      self.rcmodeu = self.rcmode.upper()

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
