###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re
import slash

from ....lib.ffmpeg.encoderbase import BaseEncoderTest
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel
from ....lib.ffmpeg.qsv.util import mapprofile, using_compatible_driver, have_encode_main10sp

@slash.requires(*have_ffmpeg_hwaccel("qsv"))
@slash.requires(using_compatible_driver)
class EncoderTest(BaseEncoderTest):
  def before(self):
    super().before()
    self.hwaccel = "qsv"
    self.hwframes = 120

  def map_profile(self):
    return mapprofile(self.codec, self.profile)

  def gen_qp_opts(self):
    if self.codec in ["mpeg2"]:
      return " -q {mqp}"
    return " -q {qp}"

  def gen_quality_opts(self):
    if self.codec in ["jpeg"]:
      return " -global_quality {quality}"
    return " -preset {quality}"

  def validate_caps(self):
    super().validate_caps()
    if vars(self).get("profile", None) in ["main10sp"] and not have_encode_main10sp(self.ffencoder):
      slash.skip_test(f"{self.ffencoder} main10sp not supported")

  def check_output(self):
    m = re.search("Initialize MFX session", self.output, re.MULTILINE)
    assert m is not None, "It appears that the QSV plugin did not load"

    if vars(self).get("ladepth", None) is not None:
      m = re.search(r"Using the VBR with lookahead \(LA\) ratecontrol method", self.output, re.MULTILINE)
      assert m is not None, "It appears that the lookahead did not load"

    if vars(self).get("profile", None) in ["main10sp"]:
      m = re.search(r"Main10sp.*: enable", self.output, re.MULTILINE)
      assert m is not None, "It appears that main10sp did not get enabled"
