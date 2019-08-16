###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

spec = load_test_spec("mpeg2", "encode")
spec_r2r = load_test_spec("mpeg2", "encode", "r2r")

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
  def init(self, tspec, case, gop, bframes, qp, quality, profile):
    self.caps = platform.get_caps("encode", "mpeg2")
    vars(self).update(tspec[case].copy())
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

  @slash.requires(*platform.have_caps("encode", "mpeg2"))
  @slash.requires(*have_gst_element("msdkmpeg2enc"))
  @slash.requires(*have_gst_element("msdkmpeg2dec"))
  @slash.parametrize(*gen_mpeg2_cqp_parameters(spec, ['high', 'main', 'simple']))
  def test(self, case, gop, bframes, qp, quality, profile):
    self.init(spec, case, gop, bframes, qp, quality, profile)
    self.encode()

  @slash.requires(*platform.have_caps("encode", "mpeg2"))
  @slash.requires(*have_gst_element("msdkmpeg2enc"))
  @slash.parametrize(*gen_mpeg2_cqp_parameters(spec_r2r, ['high', 'main', 'simple']))
  def test_r2r(self, case, gop, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()
