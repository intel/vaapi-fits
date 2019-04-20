###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

spec = load_test_spec("jpeg", "encode")
class JPEGEncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec         = "jpeg",
      gstencoder    = "msdkmjpegenc",
      gstdecoder    = "jpegparse ! msdkmjpegdec hardware=true",
      gstmediatype  = "image/jpeg",
      gstparser     = "jpegparse",
      profile       = "baseline",
    )
    super(JPEGEncoderTest, self).before()

  def get_file_ext(self):
    return "jpg"

class cqp(JPEGEncoderTest):
  @platform_tags(JPEG_ENCODE_PLATFORMS)
  @slash.requires(have_gst_msdkmjpegenc)
  @slash.requires(have_gst_msdkmjpegdec)
  @slash.parametrize(*gen_jpeg_cqp_parameters(spec))
  def test(self, case, quality):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      quality = quality,
      rcmode  = "cqp",
    )
    self.encode()
