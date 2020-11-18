###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.msdk.util import *
from ....lib.gstreamer.msdk.encoder import EncoderTest

spec      = load_test_spec("hevc", "encode", "8bit")
spec_r2r  = load_test_spec("hevc", "encode", "8bit", "r2r")

class HEVC8EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec         = "hevc-8",
      gstencoder    = "msdkh265enc",
      gstdecoder    = "h265parse ! msdkh265dec hardware=true",
      gstmediatype  = "video/x-h265",
      gstparser     = "h265parse",
      lowpower      = False,
    )
    super(HEVC8EncoderTest, self).before()

  def get_file_ext(self):
    return "h265"

class cqp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
    self.caps = platform.get_caps("encode", "hevc_8")
    vars(self).update(tspec[case].copy())
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

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.requires(*have_gst_element("msdkh265dec"))
  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.parametrize(*gen_hevc_cqp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cqp_lp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, qp, quality, profile):
    self.caps = platform.get_caps("vdenc", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case    = case,
      gop     = gop,
      qp      = qp,
      lowpower= True,
      quality = quality,
      profile = profile,
      rcmode  = "cqp",
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "hevc_8"))
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.requires(*have_gst_element("msdkh265dec"))
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "hevc_8"))
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
    self.caps = platform.get_caps("encode", "hevc_8")
    vars(self).update(tspec[case].copy())
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

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.requires(*have_gst_element("msdkh265dec"))
  @slash.parametrize(*gen_hevc_cbr_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.parametrize(*gen_hevc_cbr_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_lp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, profile):
    self.caps = platform.get_caps("vdenc", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      lowpower= True,
      maxrate = bitrate,
      minrate = bitrate,
      profile = profile,
      rcmode  = "cbr",
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "hevc_8"))
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.requires(*have_gst_element("msdkh265dec"))
  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "hevc_8"))
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.caps = platform.get_caps("encode", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      # target percentage 50%
      maxrate = bitrate * 2,
      minrate = bitrate,
      profile = profile,
      quality = quality,
      rcmode  = "vbr",
      refs    = refs,
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.requires(*have_gst_element("msdkh265dec"))
  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.parametrize(*gen_hevc_vbr_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_lp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.caps = platform.get_caps("vdenc", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      lowpower= True,
      # target percentage 50%
      maxrate = bitrate * 2,
      minrate = bitrate,
      profile = profile,
      quality = quality,
      rcmode  = "vbr",
      refs    = refs,
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "hevc_8"))
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.requires(*have_gst_element("msdkh265dec"))
  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "hevc_8"))
  @slash.requires(*have_gst_element("msdkh265enc"))
  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()
