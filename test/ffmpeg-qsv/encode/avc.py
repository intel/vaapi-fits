###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

spec      = load_test_spec("avc", "encode")
spec_r2r  = load_test_spec("avc", "encode", "r2r")

class AVCEncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec     = "avc",
      ffencoder = "h264_qsv",
      ffdecoder = "h264_qsv",
      lowpower  = 0,
    )
    super(AVCEncoderTest, self).before()

  def get_file_ext(self):
    return "h264"

class cqp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
    self.caps = platform.get_caps("encode", "avc")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      case      = case,
      gop       = gop,
      profile   = profile,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )

  @slash.requires(*platform.have_caps("encode", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cqp_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cqp_parameters(spec_r2r, ['high', 'main', 'baseline']))
  def test_r2r(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cqp_lp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, qp, quality, profile):
    self.caps = platform.get_caps("vdenc", "avc")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = gop,
      lowpower  = 1,
      profile   = profile,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec_r2r, ['high', 'main']))
  def test_r2r(self, case, gop, slices, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
    self.caps = platform.get_caps("encode", "avc")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      maxrate   = bitrate,
      minrate   = bitrate,
      profile   = profile,
      rcmode    = "cbr",
      slices    = slices,
    )

  @slash.requires(*platform.have_caps("encode", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cbr_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cbr_parameters(spec_r2r, ['high', 'main', 'baseline']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_lp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, profile):
    self.caps = platform.get_caps("vdenc", "avc")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      lowpower  = 1,
      maxrate   = bitrate,
      minrate   = bitrate,
      profile   = profile,
      rcmode    = "cbr",
      slices    = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec_r2r, ['high', 'main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_mfs(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile, mfs):
    self.caps = platform.get_caps("encode", "avc")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      maxrate   = bitrate,
      minrate   = bitrate,
      profile   = profile,
      rcmode    = "cbr",
      slices    = slices,
      mfs       = mfs,
    )

  @slash.requires(*platform.have_caps("encode", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cbr_mfs_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile, mfs):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile, mfs)
    self.encode()

class vbr(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.caps = platform.get_caps("encode", "avc")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      maxrate   = bitrate * 2, # target percentage 50%
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      slices    = slices,
    )

  @slash.requires(*platform.have_caps("encode", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_vbr_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_vbr_parameters(spec_r2r, ['high', 'main', 'baseline']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_lp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.caps = platform.get_caps("vdenc", "avc")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      lowpower  = 1,
      maxrate   = bitrate * 2, # target percentage 50%
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      slices    = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec_r2r, ['high', 'main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

class vbr_la(AVCEncoderTest):
  @slash.requires(*platform.have_caps("encode", "avc"))
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_vbr_la_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, bframes, bitrate, fps, quality, refs, profile, ladepth):
    self.caps = platform.get_caps("encode", "avc")
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      maxrate   = bitrate * 2, # target percentage 50%
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      ladepth   = ladepth,
    )
    self.encode()
