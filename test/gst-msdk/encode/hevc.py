###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.msdk.util import *
from ....lib.gstreamer.msdk.encoder import HEVC8EncoderTest, HEVC8EncoderLPTest

spec      = load_test_spec("hevc", "encode", "8bit")
spec_r2r  = load_test_spec("hevc", "encode", "8bit", "r2r")

class cqp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
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

  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_cqp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cqp_lp(HEVC8EncoderLPTest):
  def init(self, tspec, case, gop, slices, qp, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case    = case,
      gop     = gop,
      qp      = qp,
      quality = quality,
      profile = profile,
      rcmode  = "cqp",
      slices  = slices,
    )

  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
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

  @slash.parametrize(*gen_hevc_cbr_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_cbr_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_lp(HEVC8EncoderLPTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
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

  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
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

  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_vbr_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_lp(HEVC8EncoderLPTest):
  def before(self):
    super().before()
    vars(self).update(
      rcmode = "vbr",
    )

  def init(self, tspec, case, gop, slices, bitrate, fps, quality, refs, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      # target percentage 50%
      maxrate = bitrate * 2,
      minrate = bitrate,
      profile = profile,
      quality = quality,
      refs    = refs,
      slices  = slices,
    )

  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

  @slash.parametrize(*gen_hevc_tcbrc_parameters(spec, ['main']))
  def test_tcbrc(self, case, bitrate, fps, profile):
    framesz = bitrate / 8.0 / fps # kbyte
    vars(self).update(spec[case].copy())
    vars(self).update(
      bitrate         = bitrate,
      case            = case,
      fps             = fps,
      ldb             = "on",
      maxframesize    = framesz * 1.5,
      maxframesize_i  = framesz * 1.5,
      maxframesize_p  = framesz,
      maxrate         = bitrate * 2,
      minrate         = bitrate,
      profile         = profile,
      bframes         = 0,
    )
    self.encode()

class qvbr_lp(HEVC8EncoderLPTest):
  def before(self):
    super().before()
    vars(self).update(
      rcmode = "qvbr",
    )

  def init(self, tspec, case, gop, slices, bitrate, qp, fps, quality, refs, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      # target percentage 50%
      maxrate = bitrate * 2,
      minrate = bitrate,
      qp      = qp,
      profile = profile,
      quality = quality,
      refs    = refs,
      slices  = slices,
    )

  @slash.parametrize(*gen_hevc_qvbr_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bitrate, qp, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, qp, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_qvbr_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bitrate, qp, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, qp, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class max_frame_size(HEVC8EncoderTest):
  def init(self, tspec, case, bitrate, maxrate, fps, maxframesize, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      # target percentage 50%
      maxrate = maxrate,
      minrate = bitrate,
      profile = profile,
      rcmode  = "vbr",
      maxframesize = maxframesize,
    )

  @slash.parametrize(*gen_hevc_max_frame_size_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, bitrate, maxrate, fps, maxframesize, profile):
    self.init(spec, case, bitrate, maxrate, fps, maxframesize, profile)
    self.encode()

class intref_lp(HEVC8EncoderLPTest):
  def init(self, tspec, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode, reftype, refsize, refdist):
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
      intref     = dict(type = reftype, size = refsize, dist = refdist),
    )

  @slash.parametrize(*gen_hevc_intref_lp_parameters(spec, ['main']))
  def test(self, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode, reftype, refsize, refdist):
    self.init(spec, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode, reftype, refsize, refdist)
    self.encode()

class pict(HEVC8EncoderTest):
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
      pict      = 1,
    )

  @slash.parametrize(*gen_hevc_pict_parameters(spec, ['main']))
  def test(self, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode):
    self.init(spec, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode)
    self.encode()

class pict_lp(HEVC8EncoderLPTest):
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
      pict      = 1,
    )

  @slash.parametrize(*gen_hevc_pict_lp_parameters(spec, ['main']))
  def test(self, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode):
    self.init(spec, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode)
    self.encode()
