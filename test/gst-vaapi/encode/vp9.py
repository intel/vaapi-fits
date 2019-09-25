###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

spec = load_test_spec("vp9", "encode", "8bit")

class VP9EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec         = "vp9",
      gstencoder    = "vaapivp9enc",
      gstdecoder    = "matroskademux ! vaapivp9dec",
      gstmediatype  = "video/x-vp9",
      gstmuxer      = "matroskamux",
      lowpower      = False,
    )
    super(VP9EncoderTest, self).before()

  def get_file_ext(self):
    return "webm"

class cqp(VP9EncoderTest):
  @slash.requires(*platform.have_caps("encode", "vp9_8"))
  @slash.requires(*have_gst_element("vaapivp9enc"))
  @slash.requires(*have_gst_element("vaapivp9dec"))
  @slash.parametrize(*gen_vp9_cqp_parameters(spec))
  def test(self, case, ipmode, qp, quality, refmode, looplvl, loopshp):
    self.caps = platform.get_caps("encode", "vp9_8")
    vars(self).update(spec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      looplvl   = looplvl,
      loopshp   = loopshp,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      refmode   = refmode,
    )
    self.encode()

class cbr(VP9EncoderTest):
  @slash.requires(*platform.have_caps("encode", "vp9_8"))
  @slash.requires(*have_gst_element("vaapivp9enc"))
  @slash.requires(*have_gst_element("vaapivp9dec"))
  @slash.parametrize(*gen_vp9_cbr_parameters(spec))
  def test(self, case, gop, bitrate, fps, refmode, looplvl, loopshp):
    self.caps = platform.get_caps("encode", "vp9_8")
    vars(self).update(spec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      looplvl   = looplvl,
      loopshp   = loopshp,
      maxrate   = bitrate,
      minrate   = bitrate,
      rcmode    = "cbr",
      refmode   = refmode,
    )
    self.encode()

class vbr(VP9EncoderTest):
  @slash.requires(*platform.have_caps("encode", "vp9_8"))
  @slash.requires(*have_gst_element("vaapivp9enc"))
  @slash.requires(*have_gst_element("vaapivp9dec"))
  @slash.parametrize(*gen_vp9_vbr_parameters(spec))
  def test(self, case, gop, bitrate, fps, refmode, quality, looplvl, loopshp):
    self.caps = platform.get_caps("encode", "vp9_8")
    vars(self).update(spec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      looplvl   = looplvl,
      loopshp   = loopshp,
      ## target percentage 70% (hard-coded in gst-vaapi)
      ## gst-vaapi sets max-bitrate = bitrate and min-bitrate = bitrate * 0.70
      maxrate   = int(bitrate / 0.7),
      minrate   = bitrate,
      quality   = quality,
      rcmode    = "vbr",
      refmode   = refmode,
    )
    self.encode()
