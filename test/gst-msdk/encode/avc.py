###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

spec = load_test_spec("avc", "encode")

class AVCEncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec         = "avc",
      gstencoder    = "msdkh264enc",
      gstdecoder    = "h264parse ! msdkh264dec hardware=true",
      gstmediatype  = "video/x-h264",
      gstparser     = "h264parse",
    )
    super(AVCEncoderTest, self).before()

  def get_file_ext(self):
    return "h264"

class cqp(AVCEncoderTest):
  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(have_gst_msdkh264enc)
  @slash.requires(have_gst_msdkh264dec)
  @slash.parametrize(*gen_avc_cqp_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes   = bframes,
      case      = case,
      gop       = gop,
      lowpower  = False,
      profile   = profile,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )
    self.encode()

class cqp_lp(AVCEncoderTest):
  @platform_tags(AVC_ENCODE_CQP_LP_PLATFORMS)
  @slash.requires(have_gst_msdkh264enc)
  @slash.requires(have_gst_msdkh264dec)
  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, qp, quality, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case      = case,
      gop       = gop,
      lowpower  = True,
      profile   = profile,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )
    self.encode()

class cbr(AVCEncoderTest):
  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(have_gst_msdkh264enc)
  @slash.requires(have_gst_msdkh264dec)
  @slash.parametrize(*gen_avc_cbr_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      lowpower  = False,
      maxrate   = bitrate,
      minrate   = bitrate,
      profile   = profile,
      rcmode    = "cbr",
      slices    = slices,
    )
    self.encode()

class cbr_lp(AVCEncoderTest):
  @platform_tags(AVC_ENCODE_CBRVBR_LP_PLATFORMS)
  @slash.requires(have_gst_msdkh264enc)
  @slash.requires(have_gst_msdkh264dec)
  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      lowpower  = True,
      maxrate   = bitrate,
      minrate   = bitrate,
      profile   = profile,
      rcmode    = "cbr",
      slices    = slices,
    )
    self.encode()

class vbr(AVCEncoderTest):
  @platform_tags(AVC_ENCODE_PLATFORMS)
  @slash.requires(have_gst_msdkh264enc)
  @slash.requires(have_gst_msdkh264dec)
  @slash.parametrize(*gen_avc_vbr_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      lowpower  = False,
      # target percentage 50%
      maxrate   = bitrate * 2,
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      slices    = slices,
    )
    self.encode()

class vbr_lp(AVCEncoderTest):
  @platform_tags(AVC_ENCODE_CBRVBR_LP_PLATFORMS)
  @slash.requires(have_gst_msdkh264enc)
  @slash.requires(have_gst_msdkh264dec)
  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      lowpower  = True,
      # target percentage 50%
      maxrate   = bitrate * 2,
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      slices    = slices,
    )
    self.encode()
