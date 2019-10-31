###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from ...util import *
from ..encoder import EncoderTest

spec      = load_test_spec("hevc", "encode", "10bit")
spec_r2r  = load_test_spec("hevc", "encode", "10bit", "r2r")

class HEVC10EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec     = "hevc-10",
      ffencoder = "hevc_qsv",
      ffdecoder = "hevc_qsv",
      lowpower  = 0,
    )
    super(HEVC10EncoderTest, self).before()

  def get_file_ext(self):
    return "h265"

class cqp(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
    self.caps = platform.get_caps("encode", "hevc_10")
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

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cqp_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cqp_lp(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, qp, quality, profile):
    self.caps = platform.get_caps("vdenc", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case    = case,
      gop     = gop,
      lowpower= 1,
      profile = profile,
      qp      = qp,
      quality = quality,
      rcmode  = "cqp",
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
    self.caps = platform.get_caps("encode", "hevc_10")
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

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cbr_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cbr_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_lp(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, profile):
    self.caps = platform.get_caps("vdenc", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      lowpower= 1,
      minrate = bitrate,
      maxrate = bitrate,
      profile = profile,
      rcmode  = "cbr",
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.caps = platform.get_caps("encode", "hevc_10")
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

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_vbr_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_lp(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.caps = platform.get_caps("vdenc", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      lowpower= 1,
      maxrate = bitrate * 2, # target percentage 50%
      minrate = bitrate,
      profile = profile,
      quality = quality,
      rcmode  = "vbr",
      refs    = refs,
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_la(HEVC10EncoderTest):
  def init(self, tspec, case, bframes, bitrate, fps, quality, refs, profile, ladepth):
    self.caps = platform.get_caps("encode", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      maxrate = bitrate * 2, # target percentage 50%
      minrate = bitrate,
      profile = profile,
      quality = quality,
      rcmode  = "vbr",
      refs    = refs,
      bframes = bframes,
      ladepth = ladepth,
    )

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_vbr_la_parameters(spec, ['main10']))
  def test(self, case, bframes, bitrate, fps, quality, refs, profile, ladepth):
    self.init(spec, case, bframes, bitrate, fps, quality, refs, profile, ladepth)
    self.encode()
