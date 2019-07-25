###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .decoder import DecoderTest

spec = load_test_spec("vp9", "decode", "8bit")

class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)
    super(default, self).before()

  @platform_tags(VP9_DECODE_8BIT_PLATFORMS)
  @slash.parametrize(("case"), sorted([k for k,v in spec.items() if v["width"] <= 4096
    and v["height"] <= 4096 and v["format"] in mapsubsampling("FORMATS_420")]))
  def test(self, case):
    vars(self).update(spec[case].copy())
    self.case = case
    self.decode()

  @platform_tags(VP9_DECODE_8BIT_8K_PLATFORMS)
  @slash.parametrize(("case"), sorted([k for k,v in spec.items() if (v["width"] > 4096
    or v["height"] > 4096) and v["format"] in mapsubsampling("FORMATS_420")]))
  def test_highres(self, case):
    vars(self).update(spec[case].copy())
    self.case = case
    self.decode()

  def check_output(self):
    m = re.search("No support for codec vp9", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"
    super(default, self).check_output()
