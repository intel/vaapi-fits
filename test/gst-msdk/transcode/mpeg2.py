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
  @slash.requires(*have_gst_element("msdkh264enc"))
  @slash.requires(*have_gst_element("msdkh264dec"))
  @slash.requires(*have_gst_element("msdkmpeg2dec"))
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "avc", "hwhw"))
  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(AVC_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'h264',
      case         = case,
      mode         = 'hwhw',
      trans_type   = 'mpeg2_to_h264',
      gsttrans     = 'mpegvideoparse ! msdkmpeg2dec ! msdkh264enc ! video/x-h264,profile=main ! h264parse',
      gstdecoder1  = 'mpegvideoparse ! msdkmpeg2dec',
      gstdecoder2  = 'h264parse ! msdkh264dec',
    )
    self.transcode_1to1()

class to_hevc(TranscoderTest):
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.requires(*have_gst_element("msdkh265dec"))
  @slash.requires(*have_gst_element("msdkmpeg2dec"))
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "hevc", "hwhw"))
  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(HEVC_ENCODE_8BIT_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'h265',
      case         = case,
      mode         = 'hwhw',
      trans_type   = 'mpeg2_to_h265',
      gsttrans     = 'mpegvideoparse ! msdkmpeg2dec ! msdkh265enc ! video/x-h265,profile=main ! h265parse',
      gstdecoder1  = 'mpegvideoparse ! msdkmpeg2dec',
      gstdecoder2  = 'h265parse ! msdkh265dec',
    )
    self.transcode_1to1()

class to_mjpeg(TranscoderTest):
  @slash.requires(*have_gst_element("msdkmjpegenc"))
  @slash.requires(*have_gst_element("msdkmjpegdec"))
  @slash.requires(*have_gst_element("msdkmpeg2dec"))
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mjpeg", "hwhw"))
  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(JPEG_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'mjpeg',
      case         = case,
      mode         = 'hwhw',
      trans_type   = 'mpeg2_to_mjpeg',
      gsttrans     = 'mpegvideoparse ! msdkmpeg2dec ! msdkmjpegenc ! jpegparse',
      gstdecoder1  = 'mpegvideoparse ! msdkmpeg2dec',
      gstdecoder2  = 'jpegparse ! msdkmjpegdec',
    )
    self.transcode_1to1()

class to_mpeg2(TranscoderTest):
  @slash.requires(*have_gst_element("msdkmpeg2enc"))
  @slash.requires(*have_gst_element("msdkmpeg2dec"))
  @slash.parametrize(*gen_transcode_1to1_parameters(spec, "mpeg2", "hwhw"))
  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(MPEG2_ENCODE_PLATFORMS))
  def test_hwhw_1to1(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      dstextension = 'm2v',
      case         = case,
      mode         = 'hwhw',
      trans_type   = 'mpeg2_to_mpeg2',
      gsttrans     = 'mpegvideoparse ! msdkmpeg2dec ! msdkmpeg2enc ! mpegvideoparse',
      gstdecoder1  = 'mpegvideoparse ! msdkmpeg2dec',
      gstdecoder2  = 'mpegvideoparse ! msdkmpeg2dec',
    )
    self.transcode_1to1()
