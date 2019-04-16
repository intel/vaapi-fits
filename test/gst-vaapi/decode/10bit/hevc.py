###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from ...util import *
from ..decoder import DecoderTest

spec = load_test_spec("hevc", "decode", "10bit")

class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)
    super(default, self).before()

  @platform_tags(HEVC_DECODE_10BIT_PLATFORMS)
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(("case"), sorted([k for k,v in spec.items() if v["format"] in ["P010"]]))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case        = case,
      gstdecoder  = "h265parse ! vaapih265dec",
    )
    self.decode()

  @platform_tags(set(HEVC_DECODE_10BIT_PLATFORMS) & set(DECODE_10BIT_422_PLATFORMS))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(("case"), sorted([k for k,v in spec.items() if v["format"] in ["P210"]]))
  def test_422(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case        = case,
      gstdecoder  = "h265parse ! vaapih265dec",
    )
    self.decode()

  @platform_tags(set(HEVC_DECODE_10BIT_PLATFORMS) & set(DECODE_10BIT_444_PLATFORMS))
  @slash.requires(*have_gst_element("vaapih265dec"))
  @slash.parametrize(("case"), sorted([k for k,v in spec.items() if v["format"] in ["P410"]]))
  def test_444(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case        = case,
      gstdecoder  = "h265parse ! vaapih265dec",
    )
    self.decode()
