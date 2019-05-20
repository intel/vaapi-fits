###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

spec = load_test_spec("avc", "encode")
spec_r2r = load_test_spec("avc", "encode", "r2r")

class AVCEncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec     = "avc",
      ffencoder = "h264_qsv",
      ffdecoder = "h264_qsv",
      hwformat  = "nv12",
    )
    super(AVCEncoderTest, self).before()

  def get_file_ext(self):
    return "h264"

class cqp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      case      = case,
      gop       = gop,
      lowpower  = 0,
      profile   = profile,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )

  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cqp_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cqp_parameters(spec_r2r, ['high', 'main', 'baseline']))
  def test_r2r(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cqp_lp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, qp, quality, profile):
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

  @platform_tags(AVC_ENCODE_CQP_LP_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @platform_tags(AVC_ENCODE_CQP_LP_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec_r2r, ['high', 'main']))
  def test_r2r(self, case, gop, slices, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      lowpower  = 0,
      maxrate   = bitrate,
      minrate   = bitrate,
      profile   = profile,
      rcmode    = "cbr",
      slices    = slices,
    )

  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cbr_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cbr_parameters(spec_r2r, ['high', 'main', 'baseline']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_lp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, profile):
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

  @platform_tags(AVC_ENCODE_CBRVBR_LP_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @platform_tags(AVC_ENCODE_CBRVBR_LP_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec_r2r, ['high', 'main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      lowpower  = 0,
      maxrate   = bitrate * 2, # target percentage 50%
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      slices    = slices,
    )

  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_vbr_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_vbr_parameters(spec_r2r, ['high', 'main', 'baseline']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_lp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, quality, refs, profile):
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

  @platform_tags(AVC_ENCODE_CBRVBR_LP_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @platform_tags(AVC_ENCODE_CBRVBR_LP_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec_r2r, ['high', 'main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

class vbr_la(AVCEncoderTest):
  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("h264_qsv"))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
  @slash.parametrize(*gen_avc_vbr_la_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, bframes, bitrate, fps, quality, refs, profile, ladepth):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      lowpower  = 0,
      maxrate   = bitrate * 2, # target percentage 50%
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      ladepth   = ladepth,
    )
    self.encode()
