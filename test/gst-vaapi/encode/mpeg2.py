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
      gstencoder    = "vaapimpeg2enc",
      gstdecoder    = "mpegvideoparse ! vaapimpeg2dec",
      gstmediatype  = "video/mpeg",
      gstparser     = "mpegvideoparse",
    )
    super(MPEG2EncoderTest, self).before()

  def get_file_ext(self):
    return "m2v"

class cqp(MPEG2EncoderTest):
  @platform_tags(MPEG2_ENCODE_PLATFORMS)
  @slash.requires(*have_gst_element("vaapimpeg2enc"))
  @slash.requires(*have_gst_element("vaapimpeg2dec"))
  @slash.parametrize(*gen_mpeg2_cqp_parameters(spec, ['simple']))
  def test(self, case, gop, bframes, qp, quality, profile):
    vars(self).update(spec[case].copy())
    vars(self).update(
      bframes = bframes,
      case    = case,
      gop     = gop,
      mqp     = mapRange(qp, [0, 100], [2, 62]),
      profile = profile,
      qp      = qp,
      quality = quality,
      rcmode  = "cqp",
    )
    self.encode()
