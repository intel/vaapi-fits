###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.gstreamer.va.util import *
from .....lib.gstreamer.va.decoder import DecoderTest

spec = load_test_spec("av1", "decode", "10bit")

@slash.requires(*platform.have_caps("decode", "av1_10"))
@slash.requires(*have_gst_element("vaav1dec"))
class default(DecoderTest):
  def before(self):
    vars(self).update(
      # default metric
      metric      = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0),
      caps        = platform.get_caps("decode", "av1_10"),
      gstdecoder  = "vaav1dec",
      gstparser   = "av1parse",
    )
    super(default, self).before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())

    dxmap = {".ivf" : "ivfparse", ".webm" : "matroskademux", ".mkv" : "matroskademux", ".obu" : "av1parse"}
    ext = os.path.splitext(self.source)[1]
    dx = dxmap.get(ext, None)
    assert dx is not None, "Unrecognized source file extension {}".format(ext)

    vars(self).update(
      case        = case,
      gstdemuxer  = dx if self.gstparser not in dx else None,
    )
    self.decode()
