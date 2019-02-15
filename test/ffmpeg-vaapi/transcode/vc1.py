##
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .transcoder import TranscoderTest

spec = load_test_spec("vc1", "transcode")
class to_avc(TranscoderTest):
  @slash.requires(have_ffmpeg_h264_vaapi_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "avc", "hwhw"))
  @platform_tags(set(VC1_DECODE_PLATFORMS) & set(AVC_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'h264',
      case         = case,
      mode         = 'hwhw',
      mcodec       = 'h264_vaapi',
    )
    self.transcode_1to1()

class to_hevc(TranscoderTest):
  @slash.requires(have_ffmpeg_hevc_vaapi_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "hevc", "hwhw"))
  @platform_tags(set(VC1_DECODE_PLATFORMS) & set(HEVC_ENCODE_8BIT_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'h265',
      case         = case,
      mode         = 'hwhw',
      mcodec       = 'hevc_vaapi',
    )
    self.transcode_1to1()

class to_mjpeg(TranscoderTest):
  @slash.requires(have_ffmpeg_mjpeg_vaapi_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mjpeg", "hwhw"))
  @platform_tags(set(VC1_DECODE_PLATFORMS) & set(JPEG_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'mjpeg',
      case         = case,
      mode         = 'hwhw',
      mcodec       = 'mjpeg_vaapi',
    )
    self.transcode_1to1()

class to_mpeg2(TranscoderTest):
  @slash.requires(have_ffmpeg_mpeg2_vaapi_encode)
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mpeg2", "hwhw"))
  @platform_tags(set(VC1_DECODE_PLATFORMS) & set(MPEG2_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'm2v',
      case         = case,
      mode         = 'hwhw',
      mcodec       = 'mpeg2_vaapi',
    )
    self.transcode_1to1()
