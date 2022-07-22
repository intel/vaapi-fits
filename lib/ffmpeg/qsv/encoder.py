###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re
import slash

from ....lib.ffmpeg.encoderbase import BaseEncoderTest, Encoder as FFEncoder
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel
from ....lib.ffmpeg.qsv.util import mapprofile, using_compatible_driver, have_encode_main10sp
from ....lib.ffmpeg.qsv.decoder import Decoder
from ....lib.common import mapRangeInt

class Encoder(FFEncoder):
  hwaccel = property(lambda s: "qsv")
  tilecols = property(lambda s: s.ifprop("tilecols", " -tile_cols {tilecols}"))
  tilerows = property(lambda s: s.ifprop("tilerows", " -tile_rows {tilerows}"))

  @property
  def hwupload(self):
    return f"{super().hwupload}=extra_hw_frames=120"

  @property
  def qp(self):
    def inner(qp):
      if self.codec in ["mpeg2"]:
        mqp = mapRangeInt(qp, [0, 100], [1, 51])
        return f" -q {mqp}"
      return f" -q {qp}"
    return self.ifprop("qp", inner)

  @property
  def quality(self):
    def inner(quality):
      if self.codec in ["jpeg"]:
        return f" -global_quality {quality}"
      return f" -preset {quality}"
    return self.ifprop("quality", inner)

@slash.requires(*have_ffmpeg_hwaccel("qsv"))
@slash.requires(using_compatible_driver)
class EncoderTest(BaseEncoderTest):
  EncoderClass = Encoder
  DecoderClass = Decoder

  def map_profile(self):
    return mapprofile(self.codec, self.profile)

  def validate_caps(self):
    if vars(self).get("profile", None) in ["main10sp"] and not have_encode_main10sp(self.ffencoder):
      slash.skip_test(f"{self.ffencoder} main10sp not supported")

    # FIXME: this should go into BaseEncoderTest
    if self.rcmode in ["cbr", "vbr"]:
      # brframes, if specified, overrides "frames" for bitrate control modes
      self.frames = vars(self).get("brframes", self.frames)

    super().validate_caps()

  def check_output(self):
    m = re.search("Initialize MFX session", self.output, re.MULTILINE)
    assert m is not None, "It appears that the QSV plugin did not load"

    if vars(self).get("ladepth", None) is not None:
      m = re.search(r"Using the VBR with lookahead \(LA\) ratecontrol method", self.output, re.MULTILINE)
      assert m is not None, "It appears that the lookahead did not load"

    if vars(self).get("profile", None) in ["main10sp"]:
      m = re.search(r"Main10sp.*: enable", self.output, re.MULTILINE)
      assert m is not None, "It appears that main10sp did not get enabled"

    if vars(self).get("intref", None) is not None:
      patterns = [
        f"IntRefType: {self.intref['type']};",
        f"IntRefCycleSize: {self.intref['size']};",
        f"IntRefCycleDist: {self.intref['dist']}",
      ]

      for pattern in patterns:
        m = re.search(pattern, self.output, re.MULTILINE)
        assert m is not None, f"'{pattern}' missing in output"
