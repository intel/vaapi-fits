###
### Copyright (C) 2024 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.gstreamer.d3d11.util import *
from .....lib.gstreamer.d3d11.decoder import AV1_10DecoderTest as DecoderTest

spec = load_test_spec("av1", "decode", "10bit")

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

    dxmap = {".ivf" : "ivfparse", ".webm" : "matroskademux", ".mkv" : "matroskademux", ".obu" : "av1parse"}
    ext = os.path.splitext(self.source)[1]
    dx = dxmap.get(ext, None)
    assert dx is not None, "Unrecognized source file extension {}".format(ext)

    vars(self).update(
      case        = case,
      gstdemuxer  = dx if self.gstparser not in dx else None,
    )
    self.decode()
