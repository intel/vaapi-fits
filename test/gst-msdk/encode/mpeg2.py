###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

spec = load_test_spec("mpeg2", "encode")

class MPEG2EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec         = "mpeg2",
      gstencoder    = "msdkmpeg2enc",
      gstdecoder    = "mpegvideoparse ! msdkmpeg2dec hardware=true",
      gstmediatype  = "video/mpeg,mpegversion=2",
      gstparser     = "mpegvideoparse",
    )
    super(MPEG2EncoderTest, self).before()

  def get_file_ext(self):
    return "mpg"

class cqp(MPEG2EncoderTest):
  @platform_tags(MPEG2_ENCODE_PLATFORMS)
  @slash.requires(have_gst_msdkmpeg2enc)
  @slash.requires(have_gst_msdkmpeg2dec)
  @slash.parametrize(*gen_mpeg2_cqp_parameters(spec, ['high', 'main', 'simple']))
  def test(self, case, gop, bframes, qp, quality, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes = bframes,
      case    = case,
      gop     = gop,
      mqp     = mapRange(qp, [0, 100], [0, 51]),
      profile = profile,
      qp      = qp,
      quality = quality,
      rcmode  = "cqp",
    )
    self.encode()
