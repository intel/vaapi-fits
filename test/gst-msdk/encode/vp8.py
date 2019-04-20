###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

spec = load_test_spec("vp8", "encode")

class VP8EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec         = "vp8",
      gstencoder    = "msdkvp8enc",
      gstdecoder    = "matroskademux ! msdkvp8dec hardware=true",
      gstmediatype  = "video/vp8",
      gstmuxer      = "matroskamux",
      profile       = "version0_3",
    )
    super(VP8EncoderTest, self).before()

  def get_file_ext(self):
    return "webm"

class cqp(VP8EncoderTest):
  @platform_tags(VP8_ENCODE_PLATFORMS)
  @slash.requires(have_gst_msdkvp8enc)
  @slash.requires(have_gst_msdkvp8dec)
  @slash.parametrize(*gen_vp8_cqp_parameters(spec))
  def test(self, case, ipmode, qp, quality, looplvl, loopshp):
    if looplvl != 0 or loopshp != 0:
      # will looplvl or loopshp be supported later?
      slash.skip_test("looplvl != 0 or loopshp != 0 not supported")
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
