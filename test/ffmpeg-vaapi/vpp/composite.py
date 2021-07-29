###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.vpp import VppTest

spec = load_test_spec("vpp", "composite")

@slash.requires(*platform.have_caps("vpp", "blend"))
@slash.requires(*have_ffmpeg_filter("overlay_vaapi"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "blend"),
      metric  = dict(type = "md5"),
      vpp_op  = "composite",
    )
    super().before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case)
    self.vpp()

  def check_metrics(self):
    params = vars(self).copy()
    params["width"] = self.owidth
    params["height"] = self.oheight

    check_filesize(
      self.decoded, self.owidth, self.oheight, self.frames, self.format)
    check_metric(**params)
