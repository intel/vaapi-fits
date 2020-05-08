###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from ...util import *
from ..encoder import EncoderTest

spec      = load_test_spec("hevc", "encode", "10bit")
spec_ldb  = load_test_spec("hevc", "encode", "10bit", "ldb") #low delay b 10bit spec support
spec_r2r  = load_test_spec("hevc", "encode", "10bit", "r2r")

class HEVC10EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec         = "hevc-10",
      gstencoder    = "vaapih265enc",
      gstdecoder    = "h265parse ! vaapih265dec",
      gstmediatype  = "video/x-h265",
      gstparser     = "h265parse",
      lowpower      = False,
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
      qp      = qp,
      quality = quality,
      profile = profile,
      rcmode  = "cqp",
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
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

  @slash.requires(*platform.have_caps("vdenc", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

#hevc 10bit VME Low delay b cqp encode
class cqp_ldb(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
    self.caps = platform.get_caps("vme_lowdelayb", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      case         = case,
      gop          = gop,
      qp           = qp,
      lowdelayb    = 1,
      quality      = quality,
      profile      = profile,
      rcmode       = "cqp",
      slices       = slices,
    )

  @slash.requires(*platform.have_caps("vme_lowdelayb", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_cqp_ldb_parameters(spec_ldb, ['main10']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_ldb, case, gop, slices, bframes, qp, quality, profile)
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
      maxrate = bitrate,
      minrate = bitrate,
      profile = profile,
      rcmode  = "cbr",
      slices  = slices,
    )

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_cbr_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
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

  @slash.requires(*platform.have_caps("vdenc", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

#hevc 8bit vme low delay b encode cbr encode
class cbr_ldb(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
    self.caps = platform.get_caps("vme_lowdelayb", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes      = bframes,
      bitrate      = bitrate,
      case         = case,
      fps          = fps,
      gop          = gop,
      lowdelayb    = 1,
      maxrate      = bitrate,
      minrate      = bitrate,
      profile      = profile,
      rcmode       = "cbr",
      slices       = slices,
    )

  @slash.requires(*platform.have_caps("vme_lowdelayb", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_cbr_ldb_parameters(spec_ldb, ['main10']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_ldb, case, gop, slices, bframes, bitrate, fps, profile)
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

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
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

  @slash.requires(*platform.have_caps("vdenc", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec, ['main10']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec_r2r, ['main10']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

#hevc 10bit vme low delay b vbr encode
class vbr_ldb(HEVC10EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.caps = platform.get_caps("vme_lowdelayb", "hevc_10")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes      = bframes,
      bitrate      = bitrate,
      case         = case,
      fps          = fps,
      gop          = gop,
      lowdelayb    = 1,
      ## target percentage 70% (hard-coded in gst-vaapi)
      ## gst-vaapi sets max-bitrate = bitrate and min-bitrate = bitrate * 0.70
      maxrate      = int(bitrate / 0.7),
      minrate      = bitrate,
      profile      = profile,
      quality      = quality,
      rcmode       = "vbr",
      refs         = refs,
      slices       = slices,
    )

  @slash.requires(*platform.have_caps("vme_lowdelayb", "hevc_10"))
  @slash.requires(*have_gst_element("vaapih265enc"))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(*gen_hevc_vbr_ldb_parameters(spec_ldb, ['main10']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_ldb, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()
