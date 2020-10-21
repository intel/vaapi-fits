###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.qsv.util import *
from ....lib.ffmpeg.qsv.encoder import EncoderTest

spec      = load_test_spec("hevc", "encode", "8bit")
spec_ldb  = load_test_spec("hevc", "encode", "8bit", "ldb") #low delay b spec support
spec_r2r  = load_test_spec("hevc", "encode", "8bit", "r2r")

class HEVC8EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec     = "hevc-8",
      ffencoder = "hevc_qsv",
      ffdecoder = "hevc_qsv",
      lowpower  = 0,
    )
    super(HEVC8EncoderTest, self).before()

  def get_file_ext(self):
    return "h265"

class cqp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
    self.caps = platform.get_caps("encode", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      case    = case,
      gop     = gop,
      qp      = qp,
      quality = quality,
      profile = profile,
      rcmode  = "cqp",
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cqp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cqp_lp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, qp, quality, profile):
    self.caps = platform.get_caps("vdenc", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case     = case,
      gop      = gop,
      lowpower = 1,
      qp       = qp,
      quality  = quality,
      profile  = profile,
      rcmode   = "cqp",
      slices   = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cqp_ldb(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
    self.caps = platform.get_caps("vme_lowdelayb", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes      = bframes,
      case         = case,
      gop          = gop,
      qp           = qp,
      lowdelayb    = 1,
      quality      = quality,
      profile      = profile,
      rcmode       = "cqp",
      slices       = slices,
    )

  @slash.requires(*platform.have_caps("vme_lowdelayb", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cqp_ldb_parameters(spec_ldb, ['main']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_ldb, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

class cbr(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
    self.caps = platform.get_caps("encode", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      maxrate = bitrate,
      minrate = bitrate,
      profile = profile,
      rcmode  = "cbr",
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cbr_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cbr_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_lp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, profile):
    self.caps = platform.get_caps("vdenc", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      lowpower= 1,
      maxrate = bitrate,
      minrate = bitrate,
      profile = profile,
      rcmode  = "cbr",
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_ldb(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
    self.caps = platform.get_caps("vme_lowdelayb", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes      = bframes,
      bitrate      = bitrate,
      case         = case,
      fps          = fps,
      gop          = gop,
      lowdelayb    = 1,
      maxrate      = bitrate,
      minrate      = bitrate,
      profile      = profile,
      rcmode       = "cbr",
      slices       = slices,
    )

  @slash.requires(*platform.have_caps("vme_lowdelayb", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cbr_ldb_parameters(spec_ldb, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_ldb, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

class vbr(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.caps = platform.get_caps("encode", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      maxrate = bitrate * 2, # target percentage 50%
      minrate = bitrate,
      profile = profile,
      quality = quality,
      rcmode  = "vbr",
      refs    = refs,
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_vbr_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_lp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.caps = platform.get_caps("vdenc", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      lowpower= 1,
      maxrate = bitrate * 2, # target percentage 50%
      minrate = bitrate,
      profile = profile,
      quality = quality,
      rcmode  = "vbr",
      refs    = refs,
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_ldb(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.caps = platform.get_caps("vme_lowdelayb", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes      = bframes,
      bitrate      = bitrate,
      case         = case,
      fps          = fps,
      gop          = gop,
      lowdelayb    = 1,
      maxrate      = bitrate * 2, # target percentage 50%
      minrate      = bitrate,
      profile      = profile,
      quality      = quality,
      rcmode       = "vbr",
      refs         = refs,
      slices       = slices,
    )

  @slash.requires(*platform.have_caps("vme_lowdelayb", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_vbr_ldb_parameters(spec_ldb, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_ldb, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()
