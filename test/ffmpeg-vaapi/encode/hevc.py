###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

class HEVC8EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec   = "hevc-8",
      ffenc   = "hevc_vaapi",
      hwupfmt = "nv12",
    )
    super(HEVC8EncoderTest, self).before()

  def get_file_ext(self):
    return "h265"

  def get_vaapi_profile(self):
    return {
      "main" : "VAProfileHEVCMain",
    }[self.profile]

spec = load_test_spec("hevc", "encode", "8bit")
spec_r2r = load_test_spec("hevc", "encode", "8bit", "r2r")

class cqp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      case    = case,
      gop     = gop,
      qp      = qp,
      profile = profile,
      rcmode  = "cqp",
      slices  = slices,
    )

  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
  @slash.parametrize(*gen_hevc_cqp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cqp_lp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, qp, quality, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case     = case,
      gop      = gop,
      lowpower = 1,
      qp       = qp,
      profile  = profile,
      rcmode   = "cqp",
      slices   = slices,
    )

  @platform_tags(HEVC_ENCODE_8BIT_LP_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @platform_tags(HEVC_ENCODE_8BIT_LP_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
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

  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
  @slash.parametrize(*gen_hevc_cbr_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
  @slash.parametrize(*gen_hevc_cbr_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_lp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, profile):
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

  @platform_tags(HEVC_ENCODE_8BIT_LP_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @platform_tags(HEVC_ENCODE_8BIT_LP_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
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
      rcmode  = "vbr",
      refs    = refs,
      slices  = slices,
    )

  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
  @slash.parametrize(*gen_hevc_vbr_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_lp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, quality, refs, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
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
      rcmode  = "vbr",
      refs    = refs,
      slices  = slices,
    )

  @platform_tags(HEVC_ENCODE_8BIT_LP_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @platform_tags(HEVC_ENCODE_8BIT_LP_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()
