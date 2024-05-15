###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.encoder import VP8EncoderTest

spec     = load_test_spec("vp8", "encode")
spec_r2r = load_test_spec("vp8", "encode", "r2r")

class cqp(VP8EncoderTest):
  @slash.parametrize(*gen_vp8_cqp_parameters(spec))
  def test(self, case, ipmode, qp, quality, looplvl, loopshp):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      looplvl   = looplvl,
      loopshp   = loopshp,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
    )
    self.encode()

  @slash.parametrize(*gen_vp8_cqp_parameters(spec_r2r))
  def test_r2r(self, case, ipmode, qp, quality, looplvl, loopshp):
    vars(self).update(spec_r2r[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      looplvl   = looplvl,
      loopshp   = loopshp,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
    )
    vars(self).setdefault("r2r", 5)
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

  @slash.parametrize(*gen_vp8_cbr_parameters(spec_r2r))
  def test_r2r(self, case, gop, bitrate, fps, looplvl, loopshp):
    vars(self).update(spec_r2r[case].copy())
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
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr(VP8EncoderTest):
  @slash.parametrize(*gen_vp8_vbr_parameters(spec))
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
      quality   = quality,
      rcmode    = "vbr",
    )
    self.encode()

  @slash.parametrize(*gen_vp8_vbr_parameters(spec_r2r))
  def test_r2r(self, case, gop, bitrate, fps, quality, looplvl, loopshp):
    vars(self).update(spec_r2r[case].copy())
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
      quality   = quality,
      rcmode    = "vbr",
    )
    vars(self).setdefault("r2r", 5)
    self.encode()
