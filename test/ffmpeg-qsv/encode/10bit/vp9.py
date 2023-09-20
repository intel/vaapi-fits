###
### Copyright (C) 2019-2020 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.ffmpeg.qsv.util import *
from .....lib.ffmpeg.qsv.encoder import VP9_10EncoderLPTest

spec = load_test_spec("vp9", "encode", "10bit")

class cqp_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, ipmode, qp, quality, slices):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      qp        = qp,
      slices    = slices,
      rcmode    = "cqp",
      quality   = quality,
    )

  @parametrize_with_unused(*gen_vp9_cqp_lp_parameters(spec), ['refmode', 'loopshp', 'looplvl'])
  def test(self, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, ipmode, qp, quality, slices)
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

  @parametrize_with_unused(*gen_vp9_cbr_lp_parameters(spec), ['refmode', 'loopshp', 'looplvl'])
  def test(self, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, slices)
    self.encode()

class vbr_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, gop, bitrate, fps, slices, quality):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      quality   = quality,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      maxrate   = bitrate * 2, # target percentage 50%
      minrate   = bitrate,
      rcmode    = "vbr",
      slices    = slices,
    )

  @parametrize_with_unused(*gen_vp9_vbr_lp_parameters(spec), ['refmode', 'loopshp', 'looplvl'])
  def test(self, case, gop, bitrate, fps, slices, refmode, quality, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, slices, quality)
    self.encode()
