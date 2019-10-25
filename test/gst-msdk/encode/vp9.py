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
      gstencoder    = "msdkvp9enc",
      gstdecoder    = "ivfparse ! msdkvp9dec hardware=true",
    )
    super(VP9EncoderTest, self).before()

  def get_file_ext(self):
    return "ivf"

class cqp_lp(VP9EncoderTest):
  def init(self, tspec, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    slash.logger.notice("NOTICE: 'refmode' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'looplvl' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'loopshp' parameter unused (not supported by plugin)")
    self.caps = platform.get_caps("vdenc", "vp9_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = 30 if ipmode != 0 else 1,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      slices    = slices,
    )

  @slash.requires(*platform.have_caps("vdenc", "vp9_8"))
  @slash.requires(*have_gst_element("msdkvp9enc"))
  @slash.requires(*have_gst_element("msdkvp9dec"))
  @slash.parametrize(*gen_vp9_cqp_lp_parameters(spec))
  def test(self, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, ipmode, qp, quality, slices, refmode, looplvl, loopshp)
    self.encode()

class cbr_lp(VP9EncoderTest):
  def init(self, tspec, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    slash.logger.notice("NOTICE: 'refmode' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'looplvl' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'loopshp' parameter unused (not supported by plugin)")
    self.caps = platform.get_caps("vdenc", "vp9_8")
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

  @slash.requires(*platform.have_caps("vdenc", "vp9_8"))
  @slash.requires(*have_gst_element("msdkvp9enc"))
  @slash.requires(*have_gst_element("msdkvp9dec"))
  @slash.parametrize(*gen_vp9_cbr_lp_parameters(spec))
  def test(self, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, slices, refmode, looplvl, loopshp)
    self.encode()

class vbr_lp(VP9EncoderTest):
  def init(self, tspec, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    slash.logger.notice("NOTICE: 'refmode' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'looplvl' parameter unused (not supported by plugin)")
    slash.logger.notice("NOTICE: 'loopshp' parameter unused (not supported by plugin)")
    self.caps = platform.get_caps("vdenc", "vp9_8")
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

  @slash.requires(*platform.have_caps("vdenc", "vp9_8"))
  @slash.requires(*have_gst_element("msdkvp9enc"))
  @slash.requires(*have_gst_element("msdkvp9dec"))
  @slash.parametrize(*gen_vp9_vbr_lp_parameters(spec))
  def test(self, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp):
    self.init(spec, case, gop, bitrate, fps, quality, slices, refmode, looplvl, loopshp)
    self.encode()
