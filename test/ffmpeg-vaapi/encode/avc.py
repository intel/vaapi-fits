###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

class AVCEncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec   = "avc",
      ffenc   = "h264_vaapi",
      hwupfmt = "nv12",
    )
    super(AVCEncoderTest, self).before()

  def get_file_ext(self):
    return "h264"

  def get_vaapi_profile(self):
    return {
      "high"                  : "VAProfileH264High",
      "main"                  : "VAProfileH264Main",
      "constrained-baseline"  : "VAProfileH264ConstrainedBaseline",
    }[self.profile]

spec = load_test_spec("avc", "encode")

class cqp(AVCEncoderTest):
  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(have_ffmpeg_h264_vaapi_encode)
  @slash.parametrize(*gen_avc_cqp_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    vars(self).update(spec[case].copy())
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
    self.encode()

class cqp_lp(AVCEncoderTest):
  @platform_tags(AVC_ENCODE_LP_PLATFORMS)
  @slash.requires(have_ffmpeg_h264_vaapi_encode)
  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, qp, quality, profile):
    vars(self).update(spec[case].copy())
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
    self.encode()

class cbr(AVCEncoderTest):
  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(have_ffmpeg_h264_vaapi_encode)
  @slash.parametrize(*gen_avc_cbr_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    vars(self).update(spec[case].copy())
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
    self.encode()

class vbr(AVCEncoderTest):
  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(have_ffmpeg_h264_vaapi_encode)
  @slash.parametrize(*gen_avc_vbr_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    vars(self).update(spec[case].copy())
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
    self.encode()
