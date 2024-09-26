###
### Copyright (C) 2019-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.qsv.util import *
from ....lib.ffmpeg.qsv.encoder import AV1EncoderLPTest, AV1EncoderTest
from ....lib.ffmpeg.qsv.encoder import StringAPIEncoder

spec = load_test_spec("av1", "encode", "8bit")
spec_r2r  = load_test_spec("av1", "encode", "8bit", "r2r")

class cqp(AV1EncoderTest):
  def init(self, tspec, case, gop, bframes, tilecols, tilerows,qp, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = gop,
      bframes   = bframes,
      qp        = qp,
      rcmode    = "cqp",
      quality   = quality,
      profile   = profile,
      tilerows  = tilerows,
      tilecols  = tilecols,
    )

  @slash.parametrize(*gen_av1_cqp_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, qp, quality, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_av1_cqp_parameters(spec_r2r))
  def test_r2r(self, case, gop, bframes, tilecols, tilerows, qp, quality, profile):
    self.init(spec_r2r, case, gop, bframes, tilecols, tilerows, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

  @slash.requires(*have_ffmpeg_encoder_options("av1_qsv", "qsv_params"))
  @slash.parametrize(*gen_av1_cqp_parameters(spec, strapi=True))
  def test_strapi(self, case, gop, bframes, tilecols, tilerows, qp, quality, profile):
    self.EncoderClass = StringAPIEncoder
    self.init(spec, case, gop, bframes, tilecols, tilerows, qp, quality, profile)
    self.encode()

class icq(AV1EncoderTest):
  def init(self, tspec, case, gop, bframes, tilecols, tilerows,qp, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = gop,
      bframes   = bframes,
      qp        = qp,
      rcmode    = "icq",
      quality   = quality,
      profile   = profile,
      tilerows  = tilerows,
      tilecols  = tilecols,
    )

  @slash.parametrize(*gen_av1_icq_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, qp, quality, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_av1_icq_parameters(spec_r2r))
  def test_r2r(self, case, gop, bframes, tilecols, tilerows, qp, quality, profile):
    self.init(spec_r2r, case, gop, bframes, tilecols, tilerows, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr(AV1EncoderTest):
  def init(self, tspec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      bframes = bframes,
      maxrate = bitrate,
      minrate = bitrate,
      profile = profile,
      rcmode  = "cbr",
      tilerows  = tilerows,
      tilecols  = tilecols,
      quality   = quality,
    )

  @slash.parametrize(*gen_av1_cbr_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, bitrate, quality, fps, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    self.encode()

  @slash.parametrize(*gen_av1_cbr_parameters(spec_r2r))
  def test_r2r(self, case, gop, bframes, tilecols, tilerows, bitrate, quality, fps, profile):
    self.init(spec_r2r, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

  @slash.requires(*have_ffmpeg_encoder_options("av1_qsv", "qsv_params"))
  @slash.parametrize(*gen_av1_cbr_parameters(spec, strapi=True))
  def test_strapi(self, case, gop, bframes, tilecols, tilerows, bitrate, quality, fps, profile):
    self.EncoderClass = StringAPIEncoder
    self.init(spec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    self.encode()

class vbr(AV1EncoderTest):
  def init(self, tspec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      # target percentage 50%
      maxrate = bitrate * 2,
      minrate = bitrate,
      profile = profile,
      rcmode  = "vbr",
      tilerows  = tilerows,
      tilecols  = tilecols,
      quality   = quality,
      bframes   = bframes,
    )

  @slash.parametrize(*gen_av1_vbr_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    self.encode()

  @slash.parametrize(*gen_av1_vbr_parameters(spec_r2r))
  def test_r2r(self, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    self.init(spec_r2r, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

  @slash.requires(*have_ffmpeg_encoder_options("av1_qsv", "qsv_params"))
  @slash.parametrize(*gen_av1_vbr_parameters(spec, strapi=True))
  def test_strapi(self, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    self.EncoderClass = StringAPIEncoder
    self.init(spec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    self.encode()

class seek(AV1EncoderTest):
  def init(self, tspec, case, rcmode, bitrate, maxrate, fps, seek):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      bitrate   = bitrate,
      maxrate   = maxrate,
      minrate   = bitrate,
      rcmode    = rcmode,
      fps       = fps,
      seek      = seek,
    )

  @slash.parametrize(*gen_av1_seek_parameters(spec))
  def test(self, case, rcmode, bitrate, maxrate, fps, seek):
    self.init(spec, case, rcmode, bitrate, maxrate, fps, seek)
    self.encode()

class cqp_lp(AV1EncoderLPTest):
  def init(self, tspec, case, gop, bframes, tilecols, tilerows,qp, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = gop,
      bframes   = bframes,
      qp        = qp,
      rcmode    = "cqp",
      quality   = quality,
      profile   = profile,
      tilerows  = tilerows,
      tilecols  = tilecols,
    )

  @slash.parametrize(*gen_av1_cqp_lp_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, qp, quality, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_av1_cqp_lp_parameters(spec_r2r))
  def test_r2r(self, case, gop, bframes, tilecols, tilerows, qp, quality, profile):
    self.init(spec_r2r, case, gop, bframes, tilecols, tilerows, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

  @slash.requires(*have_ffmpeg_encoder_options("av1_qsv", "qsv_params"))
  @slash.parametrize(*gen_av1_cqp_lp_parameters(spec, strapi=True))
  def test_strapi(self, case, gop, bframes, tilecols, tilerows, qp, quality, profile):
    self.EncoderClass = StringAPIEncoder
    self.init(spec, case, gop, bframes, tilecols, tilerows, qp, quality, profile)
    self.encode()

class icq_lp(AV1EncoderLPTest):
  def init(self, tspec, case, gop, bframes, tilecols, tilerows,qp, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = gop,
      bframes   = bframes,
      qp        = qp,
      rcmode    = "icq",
      quality   = quality,
      profile   = profile,
      tilerows  = tilerows,
      tilecols  = tilecols,
    )

  @slash.parametrize(*gen_av1_icq_lp_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, qp, quality, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_av1_icq_lp_parameters(spec_r2r))
  def test_r2r(self, case, gop, bframes, tilecols, tilerows, qp, quality, profile):
    self.init(spec_r2r, case, gop, bframes, tilecols, tilerows, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_lp(AV1EncoderLPTest):
  def init(self, tspec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      bframes = bframes,
      maxrate = bitrate,
      minrate = bitrate,
      profile = profile,
      rcmode  = "cbr",
      tilerows  = tilerows,
      tilecols  = tilecols,
      quality   = quality,
    )

  @slash.parametrize(*gen_av1_cbr_lp_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, bitrate, quality, fps, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    self.encode()

  @slash.parametrize(*gen_av1_cbr_lp_parameters(spec_r2r))
  def test_r2r(self, case, gop, bframes, tilecols, tilerows, bitrate, quality, fps, profile):
    self.init(spec_r2r, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

  @slash.requires(*have_ffmpeg_encoder_options("av1_qsv", "qsv_params"))
  @slash.parametrize(*gen_av1_cbr_lp_parameters(spec, strapi=True))
  def test_strapi(self, case, gop, bframes, tilecols, tilerows, bitrate, quality, fps, profile):
    self.EncoderClass = StringAPIEncoder
    self.init(spec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    self.encode()

class vbr_lp(AV1EncoderLPTest):
  def init(self, tspec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      # target percentage 50%
      maxrate = bitrate * 2,
      minrate = bitrate,
      profile = profile,
      rcmode  = "vbr",
      tilerows  = tilerows,
      tilecols  = tilecols,
      quality   = quality,
      bframes   = bframes,
    )

  @slash.parametrize(*gen_av1_vbr_lp_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    self.encode()

  @slash.parametrize(*gen_av1_vbr_lp_parameters(spec_r2r))
  def test_r2r(self, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    self.init(spec_r2r, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

  @slash.requires(*have_ffmpeg_encoder_options("av1_qsv", "qsv_params"))
  @slash.parametrize(*gen_av1_vbr_lp_parameters(spec, strapi=True))
  def test_strapi(self, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    self.EncoderClass = StringAPIEncoder
    self.init(spec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    self.encode()

class seek_lp(AV1EncoderLPTest):
  def init(self, tspec, case, rcmode, bitrate, maxrate, fps, seek):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      bitrate   = bitrate,
      maxrate   = maxrate,
      minrate   = bitrate,
      rcmode    = rcmode,
      fps       = fps,
      seek      = seek,
    )

  @slash.parametrize(*gen_av1_seek_lp_parameters(spec))
  def test(self, case, rcmode, bitrate, maxrate, fps, seek):
    self.init(spec, case, rcmode, bitrate, maxrate, fps, seek)
    self.encode()
