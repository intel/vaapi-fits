###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from ...util import *
from ..decoder import DecoderTest

spec = load_test_spec("vp9", "decode", "10bit")

class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)
    super(default, self).before()

  @platform_tags(VP9_DECODE_10BIT_PLATFORMS)
  @slash.requires(*have_gst_element("vaapivp9dec"))
  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())

    dxmap = {".ivf" : "ivfparse", ".webm" : "matroskademux", ".mkv" : "matroskademux"}
    ext = os.path.splitext(self.source)[1]
    assert ext in dxmap.keys(), "Unrecognized source file extension {}".format(ext)

    vars(self).update(
      case        = case,
      gstdecoder  = "{} ! vaapivp9dec".format(dxmap[ext]),
    )
    self.decode()
