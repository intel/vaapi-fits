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

class cqp(HEVC8EncoderTest):
  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  @slash.requires(have_ffmpeg_hevc_vaapi_encode)
  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes = bframes,
      case    = case,
      gop     = gop,
      qp      = qp,
      profile = profile,
      rcmode  = "cqp",
      slices  = slices,
    )
    self.encode()

class cbr(HEVC8EncoderTest):
  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  @slash.requires(have_ffmpeg_hevc_vaapi_encode)
  @slash.parametrize(*gen_hevc_cbr_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    vars(self).update(spec[case].copy())
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
    self.encode()

class vbr(HEVC8EncoderTest):
  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  @slash.requires(have_ffmpeg_hevc_vaapi_encode)
  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main']))
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
