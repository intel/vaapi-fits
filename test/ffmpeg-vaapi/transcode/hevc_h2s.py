###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.transcoder import TranscoderTest

spec = load_test_spec("hevc", "h2s")

@slash.requires(*platform.have_caps("vpp", "tonemap"))
@slash.requires(*have_ffmpeg_filter_options("tonemap_vaapi", "format"))
class default(TranscoderTest):
  @slash.parametrize(("case"), sorted_by_resolution(spec))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case  = case,
      codec = "hevc",
    )
    self.transcode()
