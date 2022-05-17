###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.qsv.util import *
from ....lib.ffmpeg.qsv.encoder import EncoderTest

spec      = load_test_spec("avc", "encode")
spec_r2r  = load_test_spec("avc", "encode", "r2r")

@slash.requires(*have_ffmpeg_encoder("h264_qsv"))
@slash.requires(*have_ffmpeg_decoder("h264_qsv"))
class AVCEncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec     = "avc",
      ffencoder = "h264_qsv",
      ffdecoder = "h264_qsv",
    )

  def get_file_ext(self):
    return "h264"

@slash.requires(*platform.have_caps("encode", "avc"))
class AVCEncoderTest(AVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "avc"),
      lowpower  = 0,
    )

@slash.requires(*platform.have_caps("vdenc", "avc"))
class AVCEncoderLPTest(AVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "avc"),
      lowpower  = 1,
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

  @slash.parametrize(*gen_avc_cqp_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cqp_parameters(spec_r2r, ['high', 'main', 'baseline']))
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

  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cqp_lp_parameters(spec_r2r, ['high', 'main']))
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

  @slash.parametrize(*gen_avc_cbr_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cbr_parameters(spec_r2r, ['high', 'main', 'baseline']))
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

  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_avc_cbr_lp_parameters(spec_r2r, ['high', 'main']))
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
      maxrate   = bitrate * 2, # target percentage 50%
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      slices    = slices,
    )

  @slash.parametrize(*gen_avc_vbr_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_avc_vbr_parameters(spec_r2r, ['high', 'main', 'baseline']))
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
      maxrate   = bitrate * 2, # target percentage 50%
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      slices    = slices,
    )

  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec, ['high', 'main']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_avc_vbr_lp_parameters(spec_r2r, ['high', 'main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

# TODO: This can be moved into the vbr test class in a test_la method
class vbr_la(AVCEncoderTest):
  @slash.parametrize(*gen_avc_vbr_la_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, bframes, bitrate, fps, quality, refs, profile, ladepth):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      maxrate   = bitrate * 2, # target percentage 50%
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      ladepth   = ladepth,
    )
    self.encode()

class forced_idr(AVCEncoderTest):
  def init(self, tspec, case, rcmode, bitrate, maxrate, qp, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      rcmode     = rcmode,
      bitrate    = bitrate,
      case       = case,
      maxrate    = maxrate,
      minrate    = bitrate,
      profile    = profile,
      qp         = qp,
      quality    = quality,
      vforced_idr= 1,
    )

  @slash.parametrize(*gen_avc_forced_idr_parameters(spec, ['high', 'main', 'baseline']))
  def test(self, case, rcmode, bitrate, maxrate, qp, quality, profile):
    self.init(spec, case, rcmode, bitrate, maxrate, qp, quality, profile)
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
