###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.codecs import Codec
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.encoder import EncoderTest

spec      = load_test_spec("mpeg2", "encode")
spec_r2r  = load_test_spec("mpeg2", "encode", "r2r")

@slash.requires(*have_gst_element("vaapimpeg2enc"))
@slash.requires(*have_gst_element("vaapimpeg2dec"))
@slash.requires(*platform.have_caps("encode", "mpeg2"))
class MPEG2EncoderTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      caps          = platform.get_caps("encode", "mpeg2"),
      codec         = Codec.MPEG2,
      gstencoder    = "vaapimpeg2enc",
      gstdecoder    = "vaapimpeg2dec",
      gstmediatype  = "video/mpeg,mpegversion=2",
      gstparser     = "mpegvideoparse",
    )

  def get_file_ext(self):
    return "m2v"

class cqp(MPEG2EncoderTest):
  def init(self, tspec, case, gop, bframes, qp, quality):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      case    = case,
      gop     = gop,
      qp      = qp,
      quality = quality,
      rcmode  = "cqp",
    )

  @slash.parametrize(*gen_mpeg2_cqp_parameters(spec))
  def test(self, case, gop, bframes, qp, quality):
    self.init(spec, case, gop, bframes, qp, quality)
    self.encode()

  @slash.parametrize(*gen_mpeg2_cqp_parameters(spec_r2r))
  def test_r2r(self, case, gop, bframes, qp, quality):
    self.init(spec_r2r, case, gop, bframes, qp, quality)
    vars(self).setdefault("r2r", 5)
    self.encode()
