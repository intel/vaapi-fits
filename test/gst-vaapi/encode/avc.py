###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.encoder import EncoderTest

spec      = load_test_spec("avc", "encode")
spec_r2r  = load_test_spec("avc", "encode", "r2r")

@slash.requires(*have_gst_element("vaapih264enc"))
@slash.requires(*have_gst_element("vaapih264dec"))
class AVCEncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec         = "avc",
      gstencoder    = "vaapih264enc",
      gstdecoder    = "h264parse ! vaapih264dec",
      gstmediatype  = "video/x-h264",
      gstparser     = "h264parse",
      lowpower      = False,
    )
    super(AVCEncoderTest, self).before()

  def get_file_ext(self):
    return "h264"

@slash.requires(*platform.have_caps("encode", "avc"))
class cqp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
    self.caps = platform.get_caps("encode", "avc")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      case      = case,
      gop       = gop,
      profile   = profile,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )

  @slash.parametrize(*gen_avc_cqp_parameters(spec, ['main', 'high']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cqp_parameters(spec_r2r, ['main', 'high']))
  def test_r2r(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

@slash.requires(*platform.have_caps("vdenc", "avc"))
class cqp_lp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, qp, quality, profile):
    self.caps = platform.get_caps("vdenc", "avc")
    vars(self).update(tspec[case].copy())
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

  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec_r2r, ['high', 'main']))
  def test_r2r(self, case, gop, slices, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

@slash.requires(*platform.have_caps("encode", "avc"))
class cbr(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
    self.caps = platform.get_caps("encode", "avc")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      maxrate   = bitrate,
      minrate   = bitrate,
      profile   = profile,
      rcmode    = "cbr",
      slices    = slices,
    )

  @slash.parametrize(*gen_avc_cbr_parameters(spec, ['main', 'high']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cbr_parameters(spec_r2r, ['main', 'high']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

@slash.requires(*platform.have_caps("vdenc", "avc"))
class cbr_lp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, profile):
    self.caps = platform.get_caps("vdenc", "avc")
    vars(self).update(tspec[case].copy())
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

  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec, ['main', 'high']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec_r2r, ['main', 'high']))
  def test_r2r(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

@slash.requires(*platform.have_caps("encode", "avc"))
class vbr(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.caps = platform.get_caps("encode", "avc")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
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

  @slash.parametrize(*gen_avc_vbr_parameters(spec, ['main', 'high']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_avc_vbr_parameters(spec_r2r, ['main', 'high']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

@slash.requires(*platform.have_caps("vdenc", "avc"))
class vbr_lp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.caps = platform.get_caps("vdenc", "avc")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      lowpower  = True,
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

  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec, ['main', 'high']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec_r2r, ['main', 'high']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()
