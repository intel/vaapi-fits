###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib.common import get_media
from ....lib.gstreamer.decoderbase import BaseDecoderTest, Decoder as GstDecoder
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.va.util import mapformat, mapformatu

class Decoder(GstDecoder):
  format  = property(lambda s: mapformatu(super().format))
  pformat = property(lambda s: mapformat(super().format))

  @property
  def hwdevice(self):
   return get_media().render_device.split('/')[-1]

  @property
  def gstdecoder(self):
    #FIXME: use class template (e.g. similar to encoder) to resolve element
    # name sooner so that it can be used in slash.requires.
    #TODO: windows hwdevice > 0 is not test
    return super().gstdecoder if self.hwdevice in [ "renderD128", "0" ] else super().gstdecoder.replace("va", f"va{self.hwdevice}")

@slash.requires(*have_gst_element("va"))
class DecoderTest(BaseDecoderTest):
  DecoderClass = Decoder

  def before(self):
    super().before()

