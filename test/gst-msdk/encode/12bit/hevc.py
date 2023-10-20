###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.codecs import Codec
from .....lib.gstreamer.msdk.util import *
from .....lib.gstreamer.msdk.encoder import EncoderTest

spec = load_test_spec("hevc", "encode", "12bit")

@slash.requires(*have_gst_element("msdkh265dec"))
@slash.requires(*have_gst_element("msdkh265enc"))
class HEVC12EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = Codec.HEVC,
      gstdecoder    = "msdkh265dec",
      gstencoder    = "msdkh265enc",
      gstmediatype  = "video/x-h265",
      gstparser     = "h265parse",
    )

  def get_file_ext(self):
    return "h265"


@slash.requires(*platform.have_caps("encode", "hevc_12"))
class HEVC12EncoderTest(HEVC12EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_12"),
      lowpower  = False,
    )

class cqp(HEVC12EncoderTest):
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

  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main12']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

class cbr(HEVC12EncoderTest):
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

  @slash.parametrize(*gen_hevc_cbr_parameters(spec, ['main12']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

class vbr(HEVC12EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes   = bframes,
      bitrate   = bitrate,
      case      = case,
      fps       = fps,
      gop       = gop,
      maxrate   = bitrate * 2,
      minrate   = bitrate,
      profile   = profile,
      quality   = quality,
      rcmode    = "vbr",
      refs      = refs,
      slices    = slices,
    )

  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main12']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()
