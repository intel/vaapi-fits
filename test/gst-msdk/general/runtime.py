###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash

from ....lib.gstreamer.msdk.util import *
from ....lib.mfx.runtime import MFXRuntimeTest

@slash.requires(have_gst)
@slash.requires(*have_gst_element("msdkvpp"))
@slash.requires(using_compatible_driver)
class detect(MFXRuntimeTest):
  def test(self):
    self.check(
      "gst-launch-1.0 --no-position -vf videotestsrc ! msdkvpp ! fakesink"
    )
