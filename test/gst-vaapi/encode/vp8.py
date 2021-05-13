###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.encoder import EncoderTest

spec = load_test_spec("vp8", "encode")

@slash.requires(*have_gst_element("vaapivp8enc"))
@slash.requires(*have_gst_element("vaapivp8dec"))
class VP8EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = "vp8",
      gstencoder    = "vaapivp8enc",
      gstdecoder    = "matroskademux ! vaapivp8dec",
      gstmediatype  = "video/x-vp8",
      gstmuxer      = "matroskamux",
    )

  def get_file_ext(self):
    return "webm"

@slash.requires(*platform.have_caps("encode", "vp8"))
class VP8EncoderTest(VP8EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "vp8"),
      lowpower  = False,
    )

class cqp(VP8EncoderTest):
  @slash.parametrize(*gen_vp8_cqp_parameters(spec))
  def test(self, case, ipmode, qp, quality, looplvl, loopshp):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      looplvl   = looplvl,
      loopshp   = loopshp,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
    )
    self.encode()

class cbr(VP8EncoderTest):
  @slash.parametrize(*gen_vp8_cbr_parameters(spec))
  def test(self, case, gop, bitrate, fps, looplvl, loopshp):
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
    )
    self.encode()

class vbr(VP8EncoderTest):
  @slash.parametrize(*gen_vp8_vbr_parameters(spec))
  def test(self, case, gop, bitrate, fps, quality, looplvl, loopshp):
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
    )
    self.encode()
