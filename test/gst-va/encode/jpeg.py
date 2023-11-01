###
### Copyright (C) 2022-2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.va.util import *
from ....lib.gstreamer.va.encoder import JPEGEncoderTest

spec      = load_test_spec("jpeg", "encode")
spec_r2r  = load_test_spec("jpeg", "encode", "r2r")

class cqp(JPEGEncoderTest):
  def init(self, tspec, case, quality):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case    = case,
      quality = quality,
      rcmode  = "cqp",
    )

  @slash.parametrize(*gen_jpeg_cqp_parameters(spec))
  def test(self, case, quality):
    self.init(spec, case, quality)
    self.encode()

  @slash.parametrize(*gen_jpeg_cqp_parameters(spec_r2r))
  def test_r2r(self, case, quality):
    self.init(spec_r2r, case, quality)
    vars(self).setdefault("r2r", 5)
    self.encode()
