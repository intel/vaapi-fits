###
### Copyright (C) 2024 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.d3d11.util import *
from ....lib.gstreamer.d3d11.decoder import VP8DecoderTest as DecoderTest

spec = load_test_spec("vp8", "decode")

class default(DecoderTest):
  def before(self):
    super().before()
    vars(self).update(
      # default metric
      metric      = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0),
    )

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
