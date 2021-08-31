###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.msdk.util import *
from ....lib.gstreamer.msdk.decoder import DecoderTest

spec = load_test_spec("jpeg", "decode")
spec_r2r = load_test_spec("jpeg", "decode", "r2r")

@slash.requires(*platform.have_caps("decode", "jpeg"))
@slash.requires(*have_gst_element("msdkmjpegdec"))
class default(DecoderTest):
  def before(self):
    vars(self).update(
      # default metric
      metric      = dict(type = "ssim", miny = 0.99, minu = 0.99, minv = 0.99),
      caps        = platform.get_caps("decode", "jpeg"),
      gstdecoder  = "msdkmjpegdec",
      gstparser   = "jpegparse",
    )
    super(default, self).before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case)
    self.decode()

  @slash.parametrize(("case"), sorted(spec_r2r.keys()))
  def test_r2r(self, case):
    vars(self).update(spec_r2r[case].copy())
    vars(self).update(case = case)
    vars(self).setdefault("r2r", 5)
    self.decode()
