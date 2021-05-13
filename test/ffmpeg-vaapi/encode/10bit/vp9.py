###
### Copyright (C) 2019-2020 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.ffmpeg.vaapi.util import *
from .....lib.ffmpeg.vaapi.encoder import EncoderTest

spec = load_test_spec("vp9", "encode", "10bit")

@slash.requires(*have_ffmpeg_encoder("vp9_vaapi"))
class VP9_10EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec    = "vp9",
      ffenc    = "vp9_vaapi",
    )

  def get_file_ext(self):
    return "ivf"

  def get_vaapi_profile(self):
    return "VAProfileVP9Profile2"

@slash.requires(*platform.have_caps("vdenc", "vp9_10"))
class VP9_10EncoderLPTest(VP9_10EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "vp9_10"),
      lowpower  = 1,
    )

class cqp_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'refmode' parameter unused (not supported by plugin)")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      looplvl   = looplvl,
      loopshp   = loopshp,
      qp        = qp,
      rcmode    = "cqp",
      slices    = slices,
    )

  @slash.parametrize(*gen_vp9_cqp_lp_parameters(spec))
  def test(self, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp)
    self.encode()

class cbr_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    slash.logger.notice("NOTICE: 'refmode' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'looplvl' parameter unused (not supported by plugin)")
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

  @slash.parametrize(*gen_vp9_cbr_lp_parameters(spec))
  def test(self, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp)
    self.encode()

class vbr_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'refmode' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'looplvl' parameter unused (not supported by plugin)")
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
      rcmode    = "vbr",
      slices    = slices,
    )

  @slash.parametrize(*gen_vp9_vbr_lp_parameters(spec))
  def test(self, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp)
    self.encode()


