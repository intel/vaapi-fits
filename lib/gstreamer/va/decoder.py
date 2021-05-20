###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.common import get_media
from ....lib.gstreamer.decoderbase import BaseDecoderTest
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.va.util import mapformatu

@slash.requires(*have_gst_element("va"))
class DecoderTest(BaseDecoderTest):
  def before(self):
    super().before()
    # TODO: need gst-va to fix target render device

  def map_formatu(self):
    return mapformatu(self.format)
