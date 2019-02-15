###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .transcoder import TranscoderTest

spec = load_test_spec("avc", "transcode")
class to_avc(TranscoderTest):
  @slash.requires(have_ffmpeg_h264_vaapi_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "avc", "hwhw"))
  @platform_tags(set(AVC_DECODE_PLATFORMS) & set(AVC_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'h264',
      case         = case,
      mode         = 'hwhw',
      mcodec       = 'h264_vaapi',
    )
    self.transcode_1to1()
  
  @slash.requires(have_ffmpeg_x264_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "avc", "hwsw"))
  @platform_tags(AVC_DECODE_PLATFORMS)
  def test_hwsw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'h264',
      case         = case,
      mode         = 'hwsw',
      mcodec       = 'libx264',
    )
    self.transcode_1to1()
  
  @slash.requires(have_ffmpeg_h264_vaapi_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "avc", "swhw"))
  @platform_tags(AVC_ENCODE_PLATFORMS)
  def test_swhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'h264',
      case         = case,
      mode         = 'swhw',
      mcodec       = 'h264_vaapi',
    )
    self.transcode_1to1()

class to_hevc(TranscoderTest):
  @slash.requires(have_ffmpeg_hevc_vaapi_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "hevc", "hwhw"))
  @platform_tags(set(AVC_DECODE_PLATFORMS) & set(HEVC_ENCODE_8BIT_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'h265',
      case         = case,
      mode         = 'hwhw',
      mcodec       = 'hevc_vaapi',
    )
    self.transcode_1to1()

  @slash.requires(have_ffmpeg_x265_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "hevc", "hwsw"))
  @platform_tags(AVC_DECODE_PLATFORMS)
  def test_hwsw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'h265',
      case         = case,
      mode         = 'hwsw',
      mcodec       = 'libx265',
    )
    self.transcode_1to1()

  @slash.requires(have_ffmpeg_hevc_vaapi_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "hevc", "swhw"))
  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  def test_swhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'h265',
      case         = case,
      mode         = 'swhw',
      mcodec       = 'hevc_vaapi',
    )
    self.transcode_1to1()

class to_mjpeg(TranscoderTest):
  @slash.requires(have_ffmpeg_mjpeg_vaapi_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mjpeg", "hwhw"))
  @platform_tags(set(AVC_DECODE_PLATFORMS) & set(JPEG_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'mjpeg',
      case         = case,
      mode         = 'hwhw',
      mcodec       = 'mjpeg_vaapi',
    )
    self.transcode_1to1()

  @slash.requires(have_ffmpeg_mjpeg_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mjpeg", "hwsw"))
  @platform_tags(AVC_DECODE_PLATFORMS)
  def test_hwsw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'mjpeg',
      case         = case,
      mode         = 'hwsw',
      mcodec       = 'mjpeg',
    )
    self.transcode_1to1()

  @slash.requires(have_ffmpeg_mjpeg_vaapi_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mjpeg", "swhw"))
  @platform_tags(JPEG_ENCODE_PLATFORMS)
  def test_swhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'mjpeg',
      case         = case,
      mode         = 'swhw',
      mcodec       = 'mjpeg_vaapi',
    )
    self.transcode_1to1()

class to_mpeg2(TranscoderTest):
  @slash.requires(have_ffmpeg_mpeg2_vaapi_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mpeg2", "hwhw"))
  @platform_tags(set(AVC_DECODE_PLATFORMS) & set(MPEG2_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'm2v',
      case         = case,
      mode         = 'hwhw',
      mcodec       = 'mpeg2_vaapi',
    )
    self.transcode_1to1()

  @slash.requires(have_ffmpeg_mpeg2_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mpeg2", "hwsw"))
  @platform_tags(AVC_DECODE_PLATFORMS)
  def test_hwsw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'm2v',
      case         = case,
      mode         = 'hwsw',
      mcodec       = 'mpeg2video',
    )
    self.transcode_1to1()

  @slash.requires(have_ffmpeg_mpeg2_vaapi_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mpeg2", "swhw"))
  @platform_tags(MPEG2_ENCODE_PLATFORMS)
  def test_swhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'm2v',
      case         = case,
      mode         = 'swhw',
      mcodec       = 'mpeg2_vaapi',
    )
    self.transcode_1to1()
