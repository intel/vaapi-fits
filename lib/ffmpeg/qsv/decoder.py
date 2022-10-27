###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re
import slash

from ....lib.common import get_media
from ....lib.ffmpeg.decoderbase import BaseDecoderTest, Decoder as FFDecoder
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel
from ....lib.ffmpeg.qsv.util import using_compatible_driver

class Decoder(FFDecoder):
  hwaccel = property(lambda s: "qsv")

  @property
  def hwdevice(self):
    return f'qsv,child_device={get_media().render_device}'

@slash.requires(*have_ffmpeg_hwaccel("qsv"))
@slash.requires(using_compatible_driver)
class DecoderTest(BaseDecoderTest):
  DecoderClass = Decoder

  def check_output(self):
    super().check_output()

    m = re.search(
      "not supported for hardware decode", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"

    m = re.search("Initialize MFX session", self.output, re.MULTILINE)
    assert m is not None, "It appears that the QSV plugin did not load"
