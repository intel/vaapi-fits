###
### Copyright (C) 2022-2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.gstreamer.va.util import *
from .....lib.gstreamer.va.encoder import EncoderTest

spec = load_test_spec("vp9", "encode", "10bit")

@slash.requires(*have_gst_element("vavp9dec"))
class VP9_10EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = "vp9",
      gstdecoder    = "vavp9dec",
      gstmediatype  = "video/x-vp9",
      gstparser     = "vp9parse",
      gstmuxer      = "matroskamux",
      gstdemuxer    = "matroskademux",
    )

  def get_file_ext(self):
    return "webm"

@slash.requires(*have_gst_element("vavp9lpenc"))
@slash.requires(*platform.have_caps("vdenc", "vp9_10"))
class VP9_10EncoderLPTest(VP9_10EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "vp9_10"),
      lowpower  = True,
      gstencoder    = "vavp9lpenc",
    )

class cqp_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, ipmode, qp, quality, refmode, looplvl, loopshp):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      looplvl   = looplvl,
      loopshp   = loopshp,
      quality   = quality,
      rcmode    = "cqp",
    )

  @parametrize_with_unused(*gen_vp9_cqp_lp_parameters(spec), ['slices'])
  def test(self, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, ipmode, qp, quality, refmode, looplvl, loopshp)
    self.encode()

class cbr_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, gop, bitrate, fps, refmode, looplvl, loopshp):
    vars(self).update(tspec[case].copy())
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
    )

  @parametrize_with_unused(*gen_vp9_cbr_lp_parameters(spec), ['slices'])
  def test(self, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, refmode, looplvl, loopshp)
    self.encode()

class vbr_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, gop, bitrate, fps, quality, refmode, looplvl, loopshp):
    vars(self).update(tspec[case].copy())
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
      quality   = quality,
      rcmode    = "vbr",
    )

  @parametrize_with_unused(*gen_vp9_vbr_lp_parameters(spec), ['slices'])
  def test(self, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, quality, refmode, looplvl, loopshp)
    self.encode()
