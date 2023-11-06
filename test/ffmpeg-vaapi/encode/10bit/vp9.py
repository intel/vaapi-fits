###
### Copyright (C) 2019-2020 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.ffmpeg.vaapi.util import *
from .....lib.ffmpeg.vaapi.encoder import VP9_10EncoderTest, VP9_10EncoderLPTest

spec = load_test_spec("vp9", "encode", "10bit")

class cqp(VP9_10EncoderTest):
  def init(self, tspec, case, ipmode, qp, quality, slices, looplvl, loopshp):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      looplvl   = looplvl,
      loopshp   = loopshp,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_cqp_parameters(spec), ['refmode'])
  def test(self, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, ipmode, qp, quality, slices, looplvl, loopshp)
    self.encode()

class cbr(VP9_10EncoderTest):
  def init(self, tspec, case, gop, bitrate, fps, slices, loopshp):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      loopshp   = loopshp,
      maxrate   = bitrate,
      minrate   = bitrate,
      rcmode    = "cbr",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_cbr_parameters(spec), ['refmode', 'looplvl'])
  def test(self, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, slices, loopshp)
    self.encode()

class vbr(VP9_10EncoderTest):
  def init(self, tspec, case, gop, bitrate, fps, quality, slices, loopshp):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      loopshp   = loopshp,
      maxrate   = bitrate * 2, # target percentage 50%
      minrate   = bitrate,
      quality   = quality,
      rcmode    = "vbr",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_vbr_parameters(spec), ['refmode', 'looplvl'])
  def test(self, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, quality, slices, loopshp)
    self.encode()

class cqp_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, ipmode, qp, quality, slices, looplvl, loopshp):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      looplvl   = looplvl,
      loopshp   = loopshp,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_cqp_lp_parameters(spec), ['refmode'])
  def test(self, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, ipmode, qp, quality, slices, looplvl, loopshp)
    self.encode()

class cbr_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, gop, bitrate, fps, slices, loopshp):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      loopshp   = loopshp,
      maxrate   = bitrate,
      minrate   = bitrate,
      rcmode    = "cbr",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_cbr_lp_parameters(spec), ['refmode', 'looplvl'])
  def test(self, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, slices, loopshp)
    self.encode()

class vbr_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, gop, bitrate, fps, quality, slices, loopshp):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      loopshp   = loopshp,
      maxrate   = bitrate * 2, # target percentage 50%
      minrate   = bitrate,
      quality   = quality,
      rcmode    = "vbr",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_vbr_lp_parameters(spec), ['refmode', 'looplvl'])
  def test(self, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, quality, slices, loopshp)
    self.encode()


