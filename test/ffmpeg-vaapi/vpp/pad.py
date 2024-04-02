###
### Copyright (C) 2024 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.vpp import VppTest

spec = load_test_spec("vpp", "pad")
@slash.requires(*platform.have_caps("vpp", "pad"))
@slash.requires(*have_ffmpeg_filter("pad_vaapi"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "pad"),
      vpp_op  = "pad",
    )
    super().before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
    )
    self.vpp()
