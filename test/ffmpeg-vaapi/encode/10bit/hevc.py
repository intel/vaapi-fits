###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from ...util import *
from ..encoder import EncoderTest

class HEVC10EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec   = "hevc-10",
      ffenc   = "hevc_vaapi",
      hwupfmt = "p010le",
    )
    super(HEVC10EncoderTest, self).before()

  def get_file_ext(self):
    return "h265"

  def get_vaapi_profile(self):
    return {
      "main10" : "VAProfileHEVCMain10",
    }[self.profile]

spec = load_test_spec("hevc", "encode", "10bit")

class cqp(HEVC10EncoderTest):
  @platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
  @slash.requires(have_ffmpeg_hevc_vaapi_encode)
  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes = bframes,
      case    = case,
      gop     = gop,
      profile = profile,
      qp      = qp,
      rcmode  = "cqp",
      slices  = slices,
    )
    self.encode()

class cqp_lp(HEVC10EncoderTest):
  @platform_tags(HEVC_ENCODE_10BIT_LP_PLATFORMS)
  @slash.requires(have_ffmpeg_hevc_vaapi_encode)
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, qp, quality, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      gop     = gop,
      lowpower= 1,
      profile = profile,
      qp      = qp,
      rcmode  = "cqp",
      slices  = slices,
    )
    self.encode()

class cbr(HEVC10EncoderTest):
  @platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
  @slash.requires(have_ffmpeg_hevc_vaapi_encode)
  @slash.parametrize(*gen_hevc_cbr_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes = bframes,
      bitrate = bitrate,
      case = case,
      fps = fps,
      gop = gop,
      minrate = bitrate,
      maxrate = bitrate,
      profile = profile,
      rcmode = "cbr",
      slices = slices,
    )
    self.encode()

class cbr_lp(HEVC10EncoderTest):
  @platform_tags(HEVC_ENCODE_10BIT_LP_PLATFORMS)
  @slash.requires(have_ffmpeg_hevc_vaapi_encode)
  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case = case,
      fps = fps,
      gop = gop,
      lowpower= 1,
      minrate = bitrate,
      maxrate = bitrate,
      profile = profile,
      rcmode = "cbr",
      slices = slices,
    )
    self.encode()

class vbr(HEVC10EncoderTest):
  @platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
  @slash.requires(have_ffmpeg_hevc_vaapi_encode)
  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes = bframes,
      bitrate = bitrate,
      case = case,
      fps = fps,
      gop = gop,
      maxrate = bitrate * 2, # target percentage 50%
      minrate = bitrate,
      profile = profile,
      rcmode = "vbr",
      refs = refs,
      slices = slices,
    )
    self.encode()

class vbr_lp(HEVC10EncoderTest):
  @platform_tags(HEVC_ENCODE_10BIT_LP_PLATFORMS)
  @slash.requires(have_ffmpeg_hevc_vaapi_encode)
  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    vars(self).update(spec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case = case,
      fps = fps,
      gop = gop,
      lowpower= 1,
      maxrate = bitrate * 2, # target percentage 50%
      minrate = bitrate,
      profile = profile,
      rcmode = "vbr",
      refs = refs,
      slices = slices,
    )
    self.encode()
