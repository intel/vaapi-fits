###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.common import get_media
from ....lib.gstreamer.decoderbase import BaseDecoderTest
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.msdk.util import mapformatu, using_compatible_driver

@slash.requires(*have_gst_element("msdk"))
@slash.requires(using_compatible_driver)
class DecoderTest(BaseDecoderTest):
  def before(self):
    super().before()
    os.environ["GST_MSDK_DRM_DEVICE"] = get_media().render_device

  def map_formatu(self):
    return mapformatu(self.format)
