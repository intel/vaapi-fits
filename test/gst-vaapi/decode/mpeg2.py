###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .decoder import DecoderTest

spec = load_test_spec("mpeg2", "decode")
spec_r2r = load_test_spec("mpeg2", "decode", "r2r")

class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 0.99, minu = 0.99, minv = 0.99)
    super(default, self).before()

  @platform_tags(MPEG2_DECODE_PLATFORMS)
  @slash.requires(*have_gst_element("vaapimpeg2dec"))
  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case        = case,
      gstdecoder  = "mpegvideoparse ! vaapimpeg2dec",
    )
    self.decode()

  @platform_tags(MPEG2_DECODE_PLATFORMS)
  @slash.requires(*have_gst_element("vaapimpeg2dec"))
  @slash.parametrize(("case"), sorted(spec_r2r.keys()))
  def test_r2r(self, case):
    vars(self).update(spec_r2r[case].copy())
    vars(self).update(
      case        = case,
      gstdecoder  = "mpegvideoparse ! vaapimpeg2dec",
    )
    vars(self).setdefault("r2r", 5)
    self.decode()
