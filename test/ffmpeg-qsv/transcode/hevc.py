###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .transcoder import TranscoderTest

spec = load_test_spec("hevc", "transcode")
class to_avc(TranscoderTest):
  @slash.requires(have_ffmpeg_hevc_qsv_decode)
  @slash.requires(have_ffmpeg_h264_qsv_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "avc", "hwhw"))
  @platform_tags(set(HEVC_DECODE_8BIT_PLATFORMS) & set(AVC_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'h264',
      ffdecoder    = 'hevc_qsv',
      ffencoder    = 'h264_qsv',
      mode         = 'hwhw',
    )
    self.transcode_1to1()
 
  @slash.requires(have_ffmpeg_hevc_qsv_decode)
  @slash.requires(have_ffmpeg_x264_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "avc", "hwsw"))
  @platform_tags(HEVC_DECODE_8BIT_PLATFORMS)
  def test_hwsw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'h264',
      ffdecoder    = 'hevc_qsv',
      ffencoder    = 'libx264',
      mode         = 'hwsw',
    )
    self.transcode_1to1()
 
  @slash.requires(have_ffmpeg_hevc_decode)
  @slash.requires(have_ffmpeg_h264_qsv_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "avc", "swhw"))
  @platform_tags(AVC_ENCODE_PLATFORMS)
  def test_swhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'h264',
      ffdecoder    = 'hevc',
      ffencoder    = 'h264_qsv',
      mode         = 'swhw',
    )
    self.transcode_1to1()

class to_hevc(TranscoderTest):
  @slash.requires(have_ffmpeg_hevc_qsv_decode)
  @slash.requires(have_ffmpeg_hevc_qsv_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "hevc", "hwhw"))
  @platform_tags(set(HEVC_DECODE_8BIT_PLATFORMS) & set(HEVC_ENCODE_8BIT_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'h265',
      ffdecoder    = 'hevc_qsv',
      ffencoder    = 'hevc_qsv',
      mode         = 'hwhw',
    )
    self.transcode_1to1()

  @slash.requires(have_ffmpeg_hevc_qsv_decode)
  @slash.requires(have_ffmpeg_x265_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "hevc", "hwsw"))
  @platform_tags(HEVC_DECODE_8BIT_PLATFORMS)
  def test_hwsw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'h265',
      ffdecoder    = 'hevc_qsv',
      ffencoder    = 'libx265',
      mode         = 'hwsw',
    )
    self.transcode_1to1()

  @slash.requires(have_ffmpeg_hevc_decode)
  @slash.requires(have_ffmpeg_hevc_qsv_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "hevc", "swhw"))
  @platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
  def test_swhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'h265',
      ffdecoder    = 'hevc',
      ffencoder    = 'hevc_qsv',
      mode         = 'swhw',
    )
    self.transcode_1to1()

class to_mjpeg(TranscoderTest):
  @slash.requires(have_ffmpeg_hevc_qsv_decode)
  @slash.requires(have_ffmpeg_mjpeg_qsv_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mjpeg", "hwhw"))
  @platform_tags(set(HEVC_DECODE_8BIT_PLATFORMS) & set(JPEG_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'mjpeg',
      ffdecoder    = 'hevc_qsv',
      ffencoder    = 'mjpeg_qsv',
      mode         = 'hwhw',
    )
    self.transcode_1to1()

  @slash.requires(have_ffmpeg_hevc_qsv_decode)
  @slash.requires(have_ffmpeg_mjpeg_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mjpeg", "hwsw"))
  @platform_tags(HEVC_DECODE_8BIT_PLATFORMS)
  def test_hwsw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'mjpeg',
      ffdecoder    = 'hevc_qsv',
      ffencoder    = 'mjpeg',
      mode         = 'hwsw',
    )
    self.transcode_1to1()

  @slash.requires(have_ffmpeg_hevc_decode)
  @slash.requires(have_ffmpeg_mjpeg_qsv_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mjpeg", "swhw"))
  @platform_tags(JPEG_ENCODE_PLATFORMS)
  def test_swhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'mjpeg',
      ffdecoder    = 'hevc',
      ffencoder    = 'mjpeg_qsv',
      mode         = 'swhw',
    )
    self.transcode_1to1()

class to_mpeg2(TranscoderTest):
  @slash.requires(have_ffmpeg_hevc_qsv_decode)
  @slash.requires(have_ffmpeg_mpeg2_qsv_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mpeg2", "hwhw"))
  @platform_tags(set(HEVC_DECODE_8BIT_PLATFORMS) & set(MPEG2_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'm2v',
      ffdecoder    = 'hevc_qsv',
      ffencoder    = 'mpeg2_qsv',
      mode         = 'hwhw',
    )
    self.transcode_1to1()

  @slash.requires(have_ffmpeg_hevc_qsv_decode)
  @slash.requires(have_ffmpeg_mpeg2_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mpeg2", "hwsw"))
  @platform_tags(HEVC_DECODE_8BIT_PLATFORMS)
  def test_hwsw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'm2v',
      ffdecoder    = 'hevc_qsv',
      ffencoder    = 'mpeg2video',
      mode         = 'hwsw',
    )
    self.transcode_1to1()

  @slash.requires(have_ffmpeg_hevc_decode)
  @slash.requires(have_ffmpeg_mpeg2_qsv_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mpeg2", "swhw"))
  @platform_tags(MPEG2_ENCODE_PLATFORMS)
  def test_swhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'm2v',
      ffdecoder    = 'hevc',
      ffencoder    = 'mpeg2_qsv',
      mode         = 'swhw',
    )
    self.transcode_1to1()
