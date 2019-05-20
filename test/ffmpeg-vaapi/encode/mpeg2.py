###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

class MPEG2EncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec   = "mpeg2",
      ffenc   = "mpeg2_vaapi",
      hwupfmt = "nv12",
    )
    super(MPEG2EncoderTest, self).before()

  def get_file_ext(self):
    return "m2v"

  def get_vaapi_profile(self):
    return {
      "simple"  : "VAProfileMPEG2Simple",
      "main"    : "VAProfileMPEG2Main",
    }[self.profile]

spec = load_test_spec("mpeg2", "encode")
spec_r2r = load_test_spec("mpeg2", "encode", "r2r")

class cqp(MPEG2EncoderTest):
  def init(self, tspec, case, gop, bframes, qp, quality, profile):
    slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      case    = case,
      gop     = gop,
      profile = profile,
      qp      = qp,
      mqp     = mapRange(qp, [0, 100], [1, 31]),
      rcmode  = "cqp",
    )

  @platform_tags(MPEG2_ENCODE_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("mpeg2_vaapi"))
  @slash.parametrize(*gen_mpeg2_cqp_parameters(spec, ['main', 'simple']))
  def test(self, case, gop, bframes, qp, quality, profile):
    self.init(spec, case, gop, bframes, qp, quality, profile)
    self.encode()

  @platform_tags(MPEG2_ENCODE_PLATFORMS)
  @slash.requires(*have_ffmpeg_encoder("mpeg2_vaapi"))
  @slash.parametrize(*gen_mpeg2_cqp_parameters(spec_r2r, ['main', 'simple']))
  def test_r2r(self, case, gop, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()
