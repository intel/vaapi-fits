###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.decoder import DecoderTest

spec = load_test_spec("vc1", "decode")
spec_r2r = load_test_spec("vc1", "decode", "r2r")

@slash.requires(*platform.have_caps("decode", "vc1"))
@slash.requires(*have_gst_element("vaapivc1dec"))
class default(DecoderTest):
  def before(self):
    super().before()
    vars(self).update(
      # default metric
      metric      = dict(type = "ssim", miny = 0.99, minu = 0.99, minv = 0.99),
      caps        = platform.get_caps("decode", "vc1"),
      gstdecoder  = "vaapivc1dec",
      gstparser   = "'video/x-wmv,profile=(string)advanced'"
                    ",width={width},height={height},framerate=14/1",
    )

  def init(self, tspec, case):
    vars(self).update(tspec[case].copy())
    vars(self).update(case = case)
    self.gstparser = self.gstparser.format(**vars(self))

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    self.init(spec, case)
    self.decode()

  @slash.parametrize(("case"), sorted(spec_r2r.keys()))
  def test_r2r(self, case):
    self.init(spec_r2r, case)
    vars(self).setdefault("r2r", 5)
    self.decode()
