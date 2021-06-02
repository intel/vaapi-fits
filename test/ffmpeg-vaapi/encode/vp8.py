###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.encoder import EncoderTest

spec = load_test_spec("vp8", "encode")

@slash.requires(*have_ffmpeg_encoder("vp8_vaapi"))
class VP8EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec   = "vp8",
      ffenc   = "vp8_vaapi",
    )

  def get_file_ext(self):
    return "ivf"

  def get_vaapi_profile(self):
    return "VAProfileVP8Version0_3"

@slash.requires(*platform.have_caps("encode", "vp8"))
class VP8EncoderTest(VP8EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "vp8"),
      lowpower  = 0,
    )

class cqp(VP8EncoderTest):
  @parametrize_with_unused(*gen_vp8_cqp_parameters(spec), ['quality'])
  def test(self, case, ipmode, qp, quality, looplvl, loopshp):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      looplvl   = looplvl,
      loopshp   = loopshp,
      qp        = qp,
      rcmode    = "cqp",
    )
    self.encode()

class cbr(VP8EncoderTest):
  @slash.parametrize(*gen_vp8_cbr_parameters(spec))
  def test(self, case, gop, bitrate, fps, looplvl, loopshp):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      looplvl   = looplvl,
      loopshp   = loopshp,
      maxrate   = bitrate,
      minrate   = bitrate,
      rcmode    = "cbr",
    )
    self.encode()

class vbr(VP8EncoderTest):
  @parametrize_with_unused(*gen_vp8_vbr_parameters(spec), ['quality'])
  def test(self, case, gop, bitrate, fps, quality, looplvl, loopshp):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      looplvl   = looplvl,
      loopshp   = loopshp,
      maxrate   = bitrate * 2, # target percentage 50%
      minrate   = bitrate,
      rcmode    = "vbr",
    )
    self.encode()
