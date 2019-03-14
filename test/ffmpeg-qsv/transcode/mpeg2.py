##
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .transcoder import TranscoderTest

spec = load_test_spec("mpeg2", "transcode")
class to_avc(TranscoderTest):
  @slash.requires(have_ffmpeg_mpeg2_qsv_decode)
  @slash.requires(have_ffmpeg_h264_qsv_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "avc", "hwhw"))
  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(AVC_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'h264',
      ffdecoder    = 'mpeg2_qsv',
      ffencoder    = 'h264_qsv',
      mode         = 'hwhw',
    )
    self.transcode_1to1()

class to_hevc(TranscoderTest):
  @slash.requires(have_ffmpeg_mpeg2_qsv_decode)
  @slash.requires(have_ffmpeg_hevc_qsv_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "hevc", "hwhw"))
  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(HEVC_ENCODE_8BIT_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'h265',
      ffdecoder    = 'mpeg2_qsv',
      ffencoder    = 'hevc_qsv',
      mode         = 'hwhw',
    )
    self.transcode_1to1()

class to_mjpeg(TranscoderTest):
  @slash.requires(have_ffmpeg_mpeg2_qsv_decode)
  @slash.requires(have_ffmpeg_mjpeg_qsv_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mjpeg", "hwhw"))
  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(JPEG_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'mjpeg',
      ffdecoder    = 'mpeg2_qsv',
      ffencoder    = 'mjpeg_qsv',
      mode         = 'hwhw',
    )
    self.transcode_1to1()

class to_mpeg2(TranscoderTest):
  @slash.requires(have_ffmpeg_mpeg2_qsv_decode)
  @slash.requires(have_ffmpeg_mpeg2_qsv_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mpeg2", "hwhw"))
  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(MPEG2_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case         = case,
      dstextension = 'm2v',
      ffdecoder    = 'mpeg2_qsv',
      ffencoder    = 'mpeg2_qsv',
      mode         = 'hwhw',
    )
    self.transcode_1to1()
