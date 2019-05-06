###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from ...util import *
from ..encoder import EncoderTest

spec = load_test_spec("hevc", "encode", "10bit")

class HEVC10EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec         = "hevc-10",
      gstencoder    = "vaapih265enc",
      gstdecoder    = "h265parse ! vaapih265dec",
      gstmediatype  = "video/x-h265",
      gstparser     = "h265parse",
    )
    super(HEVC10EncoderTest, self).before()

  def get_file_ext(self):
    return "h265"

class cqp(HEVC10EncoderTest):
  @platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main10']))
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

class cqp_lp(HEVC10EncoderTest):
  @platform_tags(HEVC_ENCODE_10BIT_LP_PLATFORMS)
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, qp, quality, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case      = case,
      gop       = gop,
      qp        = qp,
      lowpower  = True,
      lowdelayb = 1,
      quality   = quality,
      profile   = profile,
      rcmode    = "cqp",
      slices    = slices,
    )
    self.encode()

class cbr(HEVC10EncoderTest):
  @platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_cbr_parameters(spec, ['main10']))
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

class cbr_lp(HEVC10EncoderTest):
  @platform_tags(HEVC_ENCODE_10BIT_LP_PLATFORMS)
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      lowpower  = True,
      lowdelayb = 1,
      maxrate   = bitrate,
      minrate   = bitrate,
      profile   = profile,
      rcmode    = "cbr",
      slices    = slices,
    )
    self.encode()

class vbr(HEVC10EncoderTest):
  @platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes = bframes,
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      ## target percentage 70% (hard-coded in gst-vaapi)
      ## gst-vaapi sets max-bitrate = bitrate and min-bitrate = bitrate * 0.70
      maxrate = int(bitrate / 0.7),
      minrate = bitrate,
      profile = profile,
      quality = quality,
      rcmode  = "vbr",
      refs    = refs,
      slices  = slices,
    )
    self.encode()

class vbr_lp(HEVC10EncoderTest):
  @platform_tags(HEVC_ENCODE_10BIT_LP_PLATFORMS)
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      lowpower  = True,
      lowdelayb = 1,
      ## target percentage 70% (hard-coded in gst-vaapi)
      ## gst-vaapi sets max-bitrate = bitrate and min-bitrate = bitrate * 0.70
      maxrate   = int(bitrate / 0.7),
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      slices    = slices,
    )
    self.encode()
