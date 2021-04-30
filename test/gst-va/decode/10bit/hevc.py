###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.gstreamer.vaapi.util import *
from .....lib.gstreamer.vaapi.decoder import DecoderTest

spec = load_test_spec("hevc", "decode", "10bit")

class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)
    self.caps   = platform.get_caps("decode", "hevc_10")
    super(default, self).before()

  @slash.requires(*platform.have_caps("decode", "hevc_10"))
  @slash.requires(*have_gst_element("vah265dec"))
  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case        = case,
      gstdecoder  = "h265parse ! vah265dec",
    )
    self.decode()
