###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.gstreamer.msdk.util import *
from .....lib.gstreamer.msdk.decoder import DecoderTest

spec = load_test_spec("hevc", "decode", "10bit")

@slash.requires(*platform.have_caps("decode", "hevc_10"))
@slash.requires(*have_gst_element("msdkh265dec"))
class default(DecoderTest):
  def before(self):
    super().before()
    vars(self).update(
      # default metric
      metric      = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0),
      caps        = platform.get_caps("decode", "hevc_10"),
      gstdecoder  = "msdkh265dec",
      gstparser   = "h265parse",
    )

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case)
    self.decode()
