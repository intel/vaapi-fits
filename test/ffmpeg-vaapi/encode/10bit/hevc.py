###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.ffmpeg.vaapi.util import *
from .....lib.ffmpeg.vaapi.encoder import EncoderTest

spec      = load_test_spec("hevc", "encode", "10bit")
spec_r2r  = load_test_spec("hevc", "encode", "10bit", "r2r")

@slash.requires(*have_ffmpeg_encoder("hevc_vaapi"))
class HEVC10EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec   = "hevc-10",
      ffenc   = "hevc_vaapi",
      lowpower= 0,
    )
    super(HEVC10EncoderTest, self).before()

  def get_file_ext(self):
    return "h265"

  def get_vaapi_profile(self):
    return {
      "main10"      : "VAProfileHEVCMain10",
      "main444-10"  : "VAProfileHEVCMain444_10",
    }[self.profile]

@slash.requires(*platform.have_caps("encode", "hevc_10"))
class cqp(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    self.caps = platform.get_caps("encode", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      case    = case,
      gop     = gop,
      profile = profile,
      qp      = qp,
      rcmode  = "cqp",
      slices  = slices,
    )

  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_cqp_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

@slash.requires(*platform.have_caps("vdenc", "hevc_10"))
class cqp_lp(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, qp, quality, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    self.caps = platform.get_caps("vdenc", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case    = case,
      gop     = gop,
      lowpower= 1,
      profile = profile,
      qp      = qp,
      rcmode  = "cqp",
      slices  = slices,
    )

  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

@slash.requires(*platform.have_caps("encode", "hevc_10"))
class cbr(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
    self.caps = platform.get_caps("encode", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      bitrate = bitrate,
      case = case,
      fps = fps,
      gop = gop,
      minrate = bitrate,
      maxrate = bitrate,
      profile = profile,
      rcmode = "cbr",
      slices = slices,
    )

  @slash.parametrize(*gen_hevc_cbr_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_cbr_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

@slash.requires(*platform.have_caps("vdenc", "hevc_10"))
class cbr_lp(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, profile):
    self.caps = platform.get_caps("vdenc", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case = case,
      fps = fps,
      gop = gop,
      lowpower= 1,
      minrate = bitrate,
      maxrate = bitrate,
      profile = profile,
      rcmode = "cbr",
      slices = slices,
    )

  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

@slash.requires(*platform.have_caps("encode", "hevc_10"))
class vbr(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    self.caps = platform.get_caps("encode", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      bitrate = bitrate,
      case = case,
      fps = fps,
      gop = gop,
      maxrate = bitrate * 2, # target percentage 50%
      minrate = bitrate,
      profile = profile,
      rcmode = "vbr",
      refs = refs,
      slices = slices,
    )

  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_vbr_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

@slash.requires(*platform.have_caps("vdenc", "hevc_10"))
class vbr_lp(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, quality, refs, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    self.caps = platform.get_caps("vdenc", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case = case,
      fps = fps,
      gop = gop,
      lowpower= 1,
      maxrate = bitrate * 2, # target percentage 50%
      minrate = bitrate,
      profile = profile,
      rcmode = "vbr",
      refs = refs,
      slices = slices,
    )

  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()
