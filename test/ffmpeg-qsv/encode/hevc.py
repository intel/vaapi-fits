###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

spec = load_test_spec("hevc", "encode", "8bit")

class HEVC8EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec     = "hevc-8",
      ffencoder = "hevc_qsv",
      ffdecoder = "hevc_qsv",
      hwformat  = "nv12",
    )
    super(HEVC8EncoderTest, self).before()

  def get_file_ext(self):
    return "h265"

class cqp(HEVC8EncoderTest):
  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  @slash.requires(have_ffmpeg_hevc_qsv_encode)
  @slash.requires(have_ffmpeg_hevc_qsv_decode)
  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    vars(self).update(spec[case].copy())
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
    self.encode()

class cqp_lp(HEVC8EncoderTest):
  @platform_tags(HEVC_ENCODE_8BIT_LP_PLATFORMS)
  @slash.requires(have_ffmpeg_hevc_qsv_encode)
  @slash.requires(have_ffmpeg_hevc_qsv_decode)
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, qp, quality, profile):
    vars(self).update(spec[case].copy())
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
    self.encode()

class cbr(HEVC8EncoderTest):
  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  @slash.requires(have_ffmpeg_hevc_qsv_encode)
  @slash.requires(have_ffmpeg_hevc_qsv_decode)
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
  @slash.requires(have_ffmpeg_hevc_qsv_encode)
  @slash.requires(have_ffmpeg_hevc_qsv_decode)
  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    vars(self).update(spec[case].copy())
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
    self.encode()
