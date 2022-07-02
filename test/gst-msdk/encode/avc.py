###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.msdk.util import *
from ....lib.gstreamer.msdk.encoder import EncoderTest

spec      = load_test_spec("avc", "encode")
spec_r2r  = load_test_spec("avc", "encode", "r2r")

@slash.requires(*have_gst_element("msdkh264enc"))
@slash.requires(*have_gst_element("msdkh264dec"))
class AVCEncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = "avc",
      gstencoder    = "msdkh264enc",
      gstdecoder    = "msdkh264dec",
      gstmediatype  = "video/x-h264",
      gstparser     = "h264parse",
    )

  def get_file_ext(self):
    return "h264"

@slash.requires(*platform.have_caps("encode", "avc"))
class AVCEncoderTest(AVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "avc"),
      lowpower  = False,
    )

@slash.requires(*platform.have_caps("vdenc", "avc"))
class AVCEncoderLPTest(AVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "avc"),
      lowpower  = True,
    )

class cqp(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
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

  @slash.parametrize(*gen_avc_cqp_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cqp_parameters(spec_r2r, ['main', 'high', 'constrained-baseline']))
  def test_r2r(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cqp_lp(AVCEncoderLPTest):
  def init(self, tspec, case, gop, slices, qp, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = gop,
      profile   = profile,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )

  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec_r2r, ['main', 'high', 'constrained-baseline']))
  def test_r2r(self, case, gop, slices, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
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

  @slash.parametrize(*gen_avc_cbr_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cbr_parameters(spec_r2r, ['main', 'high', 'constrained-baseline']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_lp(AVCEncoderLPTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
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

  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec_r2r, ['main', 'high', 'constrained-baseline']))
  def test_r2r(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr(AVCEncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      # target percentage 50%
      maxrate   = bitrate * 2,
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      slices    = slices,
    )

  @slash.parametrize(*gen_avc_vbr_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_avc_vbr_parameters(spec_r2r, ['main', 'high', 'constrained-baseline']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_lp(AVCEncoderLPTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, quality, refs, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      # target percentage 50%
      maxrate   = bitrate * 2,
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      slices    = slices,
    )

  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec_r2r, ['main', 'high', 'constrained-baseline']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_la(AVCEncoderTest):
  def init(self, tspec, case, bframes, bitrate, fps, quality, refs, profile, ladepth):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      # target percentage 50%
      maxrate   = bitrate * 2,
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "la_vbr",
      refs      = refs,
      ladepth   = ladepth,
    )

  @slash.parametrize(*gen_avc_vbr_la_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, bframes, bitrate, fps, quality, refs, profile, ladepth):
    self.init(spec, case, bframes, bitrate, fps, quality, refs, profile, ladepth)
    self.encode()

  @slash.parametrize(*gen_avc_vbr_la_parameters(spec_r2r, ['main', 'high', 'constrained-baseline']))
  def test_r2r(self, case, bframes, bitrate, fps, quality, refs, profile, ladepth):
    self.init(spec_r2r, case, bframes, bitrate, fps, quality, refs, profile, ladepth)
    vars(self).setdefault("r2r", 5)
    self.encode()

class max_frame_size(AVCEncoderTest):
  def init(self, tspec, case, bitrate, maxrate, fps, maxframesize, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      rcmode       = "vbr",
      bitrate      = bitrate,
      case         = case,
      maxrate      = maxrate,
      fps          = fps,
      minrate      = bitrate,
      profile      = profile,
      maxframesize = maxframesize,
    )

  @slash.parametrize(*gen_avc_max_frame_size_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, bitrate, maxrate, fps, maxframesize, profile):
    self.init(spec, case, bitrate, maxrate, fps, maxframesize, profile)
    self.encode()
