###
### Copyright (C) 2018-2020 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.ffmpeg.qsv.util import *
from .....lib.ffmpeg.qsv.decoder import DecoderTest

spec = load_test_spec("av1", "decode", "10bit")

@slash.requires(*platform.have_caps("decode", "av1_10"))
@slash.requires(*have_ffmpeg_decoder("av1_qsv"))
class default(DecoderTest):
  def before(self):
    vars(self).update(
      caps      = platform.get_caps("decode", "av1_10"),
      ffdecoder = "av1_qsv",
      # default metric
      metric    = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0),
    )
    super(default, self).before()

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case)
    self.decode()

  def check_output(self):
    m = re.search("No support for codec av1", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"
    super(default, self).check_output()
