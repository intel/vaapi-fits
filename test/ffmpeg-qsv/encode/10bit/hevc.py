###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.ffmpeg.qsv.util import *
from .....lib.ffmpeg.qsv.encoder import EncoderTest

spec      = load_test_spec("hevc", "encode", "10bit")
spec_r2r  = load_test_spec("hevc", "encode", "10bit", "r2r")

@slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
@slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
class HEVC10EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec     = "hevc-10",
      ffencoder = "hevc_qsv",
      ffdecoder = "hevc_qsv",
    )

  def get_file_ext(self):
    return "h265"

@slash.requires(*platform.have_caps("encode", "hevc_10"))
class HEVC10EncoderTest(HEVC10EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_10"),
      lowpower  = 0,
    )

@slash.requires(*platform.have_caps("vdenc", "hevc_10"))
class HEVC10EncoderLPTest(HEVC10EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "hevc_10"),
      lowpower  = 1,
    )

class cqp(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      case    = case,
      gop     = gop,
      profile = profile,
      qp      = qp,
      quality = quality,
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

class cqp_lp(HEVC10EncoderLPTest):
  def init(self, tspec, case, gop, slices, qp, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case    = case,
      gop     = gop,
      profile = profile,
      qp      = qp,
      quality = quality,
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

class cbr(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      minrate = bitrate,
      maxrate = bitrate,
      profile = profile,
      rcmode  = "cbr",
      slices  = slices,
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

class cbr_lp(HEVC10EncoderLPTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      minrate = bitrate,
      maxrate = bitrate,
      profile = profile,
      rcmode  = "cbr",
      slices  = slices,
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

class vbr(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      maxrate = bitrate * 2, # target percentage 50%
      minrate = bitrate,
      profile = profile,
      quality = quality,
      rcmode  = "vbr",
      refs    = refs,
      slices  = slices,
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

class vbr_lp(HEVC10EncoderLPTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, quality, refs, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      maxrate = bitrate * 2, # target percentage 50%
      minrate = bitrate,
      profile = profile,
      quality = quality,
      rcmode  = "vbr",
      refs    = refs,
      slices  = slices,
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

class pict(HEVC10EncoderTest):
  def init(self, tspec, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      rcmode     = rcmode,
      bframes    = bframes,
      bitrate    = bitrate,
      case       = case,
      maxrate    = maxrate,
      minrate    = bitrate,
      profile    = profile,
      qp         = qp,
      gop        = gop,
      vpict      = 1,
    )

  @slash.parametrize(*gen_hevc_pict_parameters(spec, ['main10']))
  def test(self, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode):
    self.init(spec, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode)
    self.encode()

class pict_lp(HEVC10EncoderLPTest):
  def init(self, tspec, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      rcmode     = rcmode,
      bframes    = bframes,
      bitrate    = bitrate,
      case       = case,
      maxrate    = maxrate,
      minrate    = bitrate,
      profile    = profile,
      qp         = qp,
      gop        = gop,
      vpict      = 1,
    )

  @slash.parametrize(*gen_hevc_pict_lp_parameters(spec, ['main10']))
  def test(self, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode):
    self.init(spec, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode)
    self.encode()

class roi(HEVC10EncoderTest):
  def init(self, tspec, case, gop, bframes, bitrate, maxrate, profile, rcmode):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      rcmode     = rcmode,
      bframes    = bframes,
      bitrate    = bitrate,
      case       = case,
      maxrate    = maxrate,
      minrate    = bitrate,
      profile    = profile,
      gop        = gop,
      vroi      = 1,
    )

  @slash.parametrize(*gen_hevc_roi_parameters(spec, ['main10']))
  def test(self, case, gop, bframes, bitrate, maxrate, profile, rcmode):
    self.init(spec, case, gop, bframes, bitrate, maxrate, profile, rcmode)
    self.encode()

class roi_lp(HEVC10EncoderLPTest):
  def init(self, tspec, case, gop, bframes, bitrate, maxrate, profile, rcmode):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      rcmode     = rcmode,
      bframes    = bframes,
      bitrate    = bitrate,
      case       = case,
      maxrate    = maxrate,
      minrate    = bitrate,
      profile    = profile,
      gop        = gop,
      vroi      = 1,
    )

  @slash.parametrize(*gen_hevc_roi_lp_parameters(spec, ['main10']))
  def test(self, case, gop, bframes, bitrate, maxrate, profile, rcmode):
    self.init(spec, case, gop, bframes, bitrate, maxrate, profile, rcmode)
    self.encode()
