###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.common import get_media
from ....lib.gstreamer.decoderbase import BaseDecoderTest, Decoder as GstDecoder
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.vaapi.util import mapformatu

class Decoder(GstDecoder):
  format = property(lambda s: mapformatu(super().format))

@slash.requires(*have_gst_element("vaapi"))
class DecoderTest(BaseDecoderTest):
  DecoderClass = Decoder

  def before(self):
    super().before()
    os.environ["GST_VAAPI_DRM_DEVICE"] = get_media().render_device
