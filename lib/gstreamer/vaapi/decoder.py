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
from ....lib.gstreamer.vaapi.util import mapformatu

@slash.requires(*have_gst_element("vaapi"))
class DecoderTest(BaseDecoderTest):
  def before(self):
    super().before()
    os.environ["GST_VAAPI_DRM_DEVICE"] = get_media().render_device

  def map_formatu(self):
    return mapformatu(self.format)
