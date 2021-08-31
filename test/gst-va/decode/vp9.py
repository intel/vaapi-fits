###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.decoder import DecoderTest

spec = load_test_spec("vp9", "decode", "8bit")

@slash.requires(*platform.have_caps("decode", "vp9_8"))
@slash.requires(*have_gst_element("vavp9dec"))
class default(DecoderTest):
  def before(self):
    vars(self).update(
      # default metric
      metric      = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0),
      caps        = platform.get_caps("decode", "vp9_8"),
      gstdecoder  = "vavp9dec",
      gstparser   = "vp9parse",
    )
    super(default, self).before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())

    dxmap = {".ivf" : "ivfparse", ".webm" : "matroskademux"}
    ext = os.path.splitext(self.source)[1]
    assert ext in dxmap.keys(), "Unrecognized source file extension {}".format(ext)

    vars(self).update(
      case        = case,
      gstdemuxer  = dxmap[ext],
    )
    self.decode()
