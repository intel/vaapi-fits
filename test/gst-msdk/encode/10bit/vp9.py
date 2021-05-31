###
### Copyright (C) 2019-2020 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.gstreamer.msdk.util import *
from .....lib.gstreamer.msdk.encoder import EncoderTest

spec = load_test_spec("vp9", "encode", "10bit")

@slash.requires(*have_gst_element("msdkvp9enc"))
@slash.requires(*have_gst_element("msdkvp9dec"))
class VP9_10EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = "vp9",
      gstencoder    = "msdkvp9enc",
      gstdecoder    = "matroskademux ! msdkvp9dec hardware=true",
      gstmediatype  = "video/x-vp9",
      gstmuxer      = "matroskamux",
    )

  def get_file_ext(self):
    return "webm"

@slash.requires(*platform.have_caps("vdenc", "vp9_10"))
class VP9_10EncoderLPTest(VP9_10EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps  = platform.get_caps("vdenc", "vp9_10"),
      # NOTE: msdkvp9enc does not have lowpower property.
      # msdkvp9enc lowpower is hardcoded internally
    )

class cqp_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    skip_test_by_parameter("encode/10bit/vp9/cqp_lp", ['refmode', 'looplvl', 'loopshp'],
      case      = case,
      ipmode    = ipmode,
      qp        = qp,
      quality   = quality,
      slices    = slices,
      refmode   = refmode,
      looplvl   = looplvl,
      loopshp   = loopshp,
    )
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )

  @slash.parametrize(*gen_vp9_cqp_lp_parameters(spec))
  def test(self, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp)
    self.encode()

class cbr_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    skip_test_by_parameter("encode/10bit/vp9/cbr_lp", ['refmode', 'looplvl', 'loopshp'],
      case      = case,
      gop       = gop,
      bitrate   = bitrate,
      fps       = fps,
      slices    = slices,
      refmode   = refmode,
      looplvl   = looplvl,
      loopshp   = loopshp,
    )
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      maxrate   = bitrate,
      minrate   = bitrate,
      rcmode    = "cbr",
      slices    = slices,
    )

  @slash.parametrize(*gen_vp9_cbr_lp_parameters(spec))
  def test(self, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp)
    self.encode()

class vbr_lp(VP9_10EncoderLPTest):
  def init(self, tspec, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    skip_test_by_parameter("encode/10bit/vp9/vbr_lp", ['refmode', 'looplvl', 'loopshp'],
      case      = case,
      gop       = gop,
      bitrate   = bitrate,
      fps       = fps,
      quality   = quality,
      slices    = slices,
      refmode   = refmode,
      looplvl   = looplvl,
      loopshp   = loopshp,
    )
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      frames    = vars(self).get("brframes", self.frames),
      gop       = gop,
      # target percentage 50%
      maxrate   = bitrate * 2,
      minrate   = bitrate,
      quality   = quality,
      rcmode    = "vbr",
      slices    = slices,
    )

  @slash.parametrize(*gen_vp9_vbr_lp_parameters(spec))
  def test(self, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp)
    self.encode()
