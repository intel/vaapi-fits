###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.vpp import VppTest

spec = load_test_spec("vpp", "csc")

@slash.requires(*platform.have_caps("vpp", "csc"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps        = platform.get_caps("vpp", "csc"),
      vpp_element = "csc",
    )
    super(default, self).before()

  @slash.parametrize(*gen_vpp_csc_parameters(spec))
  def test(self, case, csc):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case, csc = csc)
    self.vpp()

  def check_metrics(self):
    check_metric(
      # if user specified metric, then use it.  Otherwise, use ssim metric with perfect score
      metric = vars(self).get("metric", dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)),
      # If user specified reference, use it.  Otherwise, assume source is the reference.
      reference = format_value(self.reference, **vars(self))
        if vars(self).get("reference") else self.source,
      decoded = self.ofile,
      # if user specified reference, then assume it's format is the same as csc output format.
      # Otherwise, the format is the source format
      format = self.format if vars(self).get("reference", None) is None else self.csc,
      format2 = self.csc,
      width = self.width, height = self.height, frames = self.frames,
    )
