###
### Copyright (C) 2018-2020 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.gstreamer.msdk.util import *
from .....lib.gstreamer.msdk.decoder import DecoderTest

spec = load_test_spec("av1", "decode", "10bit")

@slash.requires(*platform.have_caps("decode", "av1_10"))
@slash.requires(*have_gst_element("msdkav1dec"))
class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)
    self.caps   = platform.get_caps("decode", "av1_10")
    super(default, self).before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())

    dxmap = {".ivf" : "ivfparse", ".webm" : "matroskademux", ".obu" : "av1parse"}
    ext = os.path.splitext(self.source)[1]
    dx = dxmap.get(ext, None)
    assert dx is not None, "Unrecognized source file extension {}".format(ext)

    if "av1parse" not in dx:
      dx += " ! av1parse"

    vars(self).update(
      case        = case,
      gstdecoder  = "{} ! msdkav1dec".format(dx),
    )
    self.decode()
