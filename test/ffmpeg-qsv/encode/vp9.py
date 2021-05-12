###
### Copyright (C) 2019-2020 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.qsv.util import *
from ....lib.ffmpeg.qsv.encoder import EncoderTest

spec = load_test_spec("vp9", "encode", "8bit")

@slash.requires(*have_ffmpeg_encoder("vp9_qsv"))
@slash.requires(*have_ffmpeg_decoder("vp9_qsv"))
class VP9EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec     = "vp9",
      ffencoder = "vp9_qsv",
      ffdecoder = "vp9_qsv",
    )
    super(VP9EncoderTest, self).before()

  def get_file_ext(self):
    return "ivf"

@slash.requires(*platform.have_caps("vdenc", "vp9_8"))
class cqp_lp(VP9EncoderTest):
  def init(self, tspec, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    slash.logger.notice("NOTICE: 'refmode' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'loopshp' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'looplvl' parameter unused (not supported by plugin)")
    self.caps = platform.get_caps("vdenc", "vp9_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      qp        = qp,
      slices    = slices,
      rcmode    = "cqp",
      quality   = quality,
      lowpower  = 1,
    )

  @slash.parametrize(*gen_vp9_cqp_lp_parameters(spec))
  def test(self, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp)
    self.encode()

@slash.requires(*platform.have_caps("vdenc", "vp9_8"))
class cbr_lp(VP9EncoderTest):
  def init(self, tspec, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    slash.logger.notice("NOTICE: 'refmode' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'loopshp' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'looplvl' parameter unused (not supported by plugin)")
    self.caps = platform.get_caps("vdenc", "vp9_8")
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
      lowpower  = 1,
    )

  @slash.parametrize(*gen_vp9_cbr_lp_parameters(spec))
  def test(self, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp)
    self.encode()

@slash.requires(*platform.have_caps("vdenc", "vp9_8"))
class vbr_lp(VP9EncoderTest):
  def init(self, tspec, case, gop, bitrate, fps, slices, refmode, quality, looplvl, loopshp):
    slash.logger.notice("NOTICE: 'refmode' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'loopshp' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'looplvl' parameter unused (not supported by plugin)")
    self.caps = platform.get_caps("vdenc", "vp9_8")
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
      lowpower  = 1,
    )

  @slash.parametrize(*gen_vp9_vbr_lp_parameters(spec))
  def test(self, case, gop, bitrate, fps, slices, refmode, quality, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, slices, refmode, quality, looplvl, loopshp)
    self.encode()

