###
### Copyright (C) 2019-2020 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.gstreamer.msdk.util import *
from .....lib.gstreamer.msdk.encoder import VP9_10EncoderTest, VP9_10EncoderLPTest

spec     = load_test_spec("vp9", "encode", "10bit")
spec_r2r = load_test_spec("vp9", "encode", "10bit", "r2r")

class cqp(VP9_10EncoderTest):
  def init(self, tspec, case, ipmode, qp, quality, slices):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_cqp_parameters(spec), ['refmode', 'looplvl', 'loopshp'])
  def test(self, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, ipmode, qp, quality, slices)
    self.encode()

  @parametrize_with_unused(*gen_vp9_cqp_parameters(spec_r2r), ['refmode', 'looplvl', 'loopshp'])
  def test_r2r(self, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    self.init(spec_r2r, case, ipmode, qp, quality, slices)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr(VP9_10EncoderTest):
  def init(self, tspec, case, gop, bitrate, fps, slices):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      maxrate   = bitrate,
      minrate   = bitrate,
      rcmode    = "cbr",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_cbr_parameters(spec), ['refmode', 'looplvl', 'loopshp'])
  def test(self, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, slices)
    self.encode()

  @parametrize_with_unused(*gen_vp9_cbr_parameters(spec_r2r), ['refmode', 'looplvl', 'loopshp'])
  def test_r2r(self, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    self.init(spec_r2r, case, gop, bitrate, fps, slices)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr(VP9_10EncoderTest):
  def init(self, tspec, case, gop, bitrate, fps, quality, slices):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      # target percentage 50%
      maxrate   = bitrate * 2,
      minrate   = bitrate,
      quality   = quality,
      rcmode    = "vbr",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_vbr_parameters(spec), ['refmode', 'looplvl', 'loopshp'])
  def test(self, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, quality, slices)
    self.encode()

  @parametrize_with_unused(*gen_vp9_vbr_parameters(spec_r2r), ['refmode', 'looplvl', 'loopshp'])
  def test_r2r(self, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    self.init(spec_r2r, case, gop, bitrate, fps, quality, slices)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cqp_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, ipmode, qp, quality, slices):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_cqp_lp_parameters(spec), ['refmode', 'looplvl', 'loopshp'])
  def test(self, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, ipmode, qp, quality, slices)
    self.encode()

  @parametrize_with_unused(*gen_vp9_cqp_lp_parameters(spec_r2r), ['refmode', 'looplvl', 'loopshp'])
  def test_r2r(self, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    self.init(spec_r2r, case, ipmode, qp, quality, slices)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, gop, bitrate, fps, slices):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      maxrate   = bitrate,
      minrate   = bitrate,
      rcmode    = "cbr",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_cbr_lp_parameters(spec), ['refmode', 'looplvl', 'loopshp'])
  def test(self, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, slices)
    self.encode()

  @parametrize_with_unused(*gen_vp9_cbr_lp_parameters(spec_r2r), ['refmode', 'looplvl', 'loopshp'])
  def test_r2r(self, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    self.init(spec_r2r, case, gop, bitrate, fps, slices)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, gop, bitrate, fps, quality, slices):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      # target percentage 50%
      maxrate   = bitrate * 2,
      minrate   = bitrate,
      quality   = quality,
      rcmode    = "vbr",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_vbr_lp_parameters(spec), ['refmode', 'looplvl', 'loopshp'])
  def test(self, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, quality, slices)
    self.encode()

  @parametrize_with_unused(*gen_vp9_vbr_lp_parameters(spec_r2r), ['refmode', 'looplvl', 'loopshp'])
  def test_r2r(self, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    self.init(spec_r2r, case, gop, bitrate, fps, quality, slices)
    vars(self).setdefault("r2r", 5)
    self.encode()
