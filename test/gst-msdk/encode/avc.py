###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.msdk.util import *
from ....lib.gstreamer.msdk.encoder import AVCEncoderTest, AVCEncoderLPTest

spec      = load_test_spec("avc", "encode")
spec_r2r  = load_test_spec("avc", "encode", "r2r")

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

  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec_r2r, ['main', 'high', 'constrained-baseline']))
  def test_r2r(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, bframes, qp, quality, profile)
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

  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec_r2r, ['main', 'high', 'constrained-baseline']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, profile)
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
  def before(self):
    super().before()
    vars(self).update(
      rcmode = "vbr",
    )

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
      refs      = refs,
      slices    = slices,
    )

  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec, ['main', 'high', 'constrained-baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec_r2r, ['main', 'high', 'constrained-baseline']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

  @slash.parametrize(*gen_avc_tcbrc_parameters(spec, ['main']))
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

class intref(AVCEncoderTest):
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

  @slash.parametrize(*gen_avc_intref_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode, reftype, refsize, refdist):
    self.init(spec, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode, reftype, refsize, refdist)
    self.encode()

class intref_lp(AVCEncoderLPTest):
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

  @slash.parametrize(*gen_avc_intref_lp_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode, reftype, refsize, refdist):
    self.init(spec, case, gop, bframes, bitrate, qp, maxrate, profile, rcmode, reftype, refsize, refdist)
    self.encode()

class rqp(AVCEncoderTest):
  def init(self, tspec, case, gop, bframes, bitrate, maxrate, profile, rcmode, maxi, mini, maxp, minp, maxb, minb):
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
      rqp        = dict(MaxQPI = maxi, MinQPI = mini, MaxQPP = maxp, MinQPP = minp, MaxQPB = maxb, MinQPB = minb),
    )

  @slash.parametrize(*gen_avc_rqp_parameters(spec, ['main']))
  def test(self, case, gop, bframes, bitrate, maxrate, profile, rcmode, maxi, mini, maxp, minp, maxb, minb):
    self.init(spec, case, gop, bframes, bitrate, maxrate, profile, rcmode, maxi, mini, maxp, minp, maxb, minb)
    self.encode()
