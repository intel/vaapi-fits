###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.qsv.util import *
from ....lib.ffmpeg.qsv.vpp import VppTest

if len(load_test_spec("vpp", "deinterlace")):
  slash.logger.warn(
    "ffmpeg-qsv: vpp deinterlace with raw input is no longer supported")

@slash.requires(*platform.have_caps("vpp", "deinterlace"))
class DeinterlaceTest(VppTest):
  _default_methods_ = [
    "bob",
    "advanced",
  ]

  _default_modes_ = [
    dict(method = m, rate = "frame") for m in _default_methods_
  ]

  def before(self):
    vars(self).update(
      metric  = dict(type = "md5"), # default metric
      vpp_op  = "deinterlace",
    )
    super().before()

  def init(self, tspec, case, method, rate):
    vars(self).update(tspec[case].copy())
    vars(self).update(case = case, method = method, rate = rate)

  def validate_caps(self):
    self.caps = platform.get_caps(
      "vpp", "deinterlace", self.method.replace('-', '_'))

    if self.caps is None:
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{method} not supported", **vars(self)))

    self.mmethod = map_deinterlace_method(self.method)

    # The rate is fixed in vpp_qsv deinterlace.  It always outputs at frame
    # rate (one frame of output for each field-pair).
    if "frame" != self.rate:
      slash.skip_test("{rate} rate not supported".format(**vars(self)))

    if self.mmethod is None:
      slash.skip_test("{method} method not supported".format(**vars(self)))

    super().validate_caps()

spec_avc      = load_test_spec("vpp", "deinterlace", "avc")
spec_avc_r2r  = load_test_spec("vpp", "deinterlace", "avc", "r2r")
@slash.requires(*platform.have_caps("decode", "avc"))
@slash.requires(*have_ffmpeg_decoder("h264_qsv"))
class avc(DeinterlaceTest):
  def before(self):
    self.ffdecoder = "h264_qsv"
    super(avc, self).before()

  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_avc, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    self.init(spec_avc, case, method, rate)
    self.vpp()

  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_avc_r2r, DeinterlaceTest._default_modes_))
  def test_r2r(self, case, method, rate):
    self.init(spec_avc_r2r, case, method, rate)
    vars(self).setdefault("r2r", 5)
    self.vpp()

spec_mpeg2      = load_test_spec("vpp", "deinterlace", "mpeg2")
spec_mpeg2_r2r  = load_test_spec("vpp", "deinterlace", "mpeg2", "r2r")
@slash.requires(*platform.have_caps("decode", "mpeg2"))
@slash.requires(*have_ffmpeg_decoder("mpeg2_qsv"))
class mpeg2(DeinterlaceTest):
  def before(self):
    self.ffdecoder = "mpeg2_qsv"
    super(mpeg2, self).before()

  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_mpeg2, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    self.init(spec_mpeg2, case, method, rate)
    self.vpp()

  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_mpeg2_r2r, DeinterlaceTest._default_modes_))
  def test_r2r(self, case, method, rate):
    self.init(spec_mpeg2_r2r, case, method, rate)
    vars(self).setdefault("r2r", 5)
    self.vpp()

spec_vc1      = load_test_spec("vpp", "deinterlace", "vc1")
spec_vc1_r2r  = load_test_spec("vpp", "deinterlace", "vc1", "r2r")
@slash.requires(*platform.have_caps("decode", "vc1"))
@slash.requires(*have_ffmpeg_decoder("vc1_qsv"))
class vc1(DeinterlaceTest):
  def before(self):
    self.ffdecoder = "vc1_qsv"
    super(vc1, self).before()

  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_vc1, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    self.init(spec_vc1, case, method, rate)
    self.vpp()

  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_vc1_r2r, DeinterlaceTest._default_modes_))
  def test_r2r(self, case, method, rate):
    self.init(spec_vc1_r2r, case, method, rate)
    vars(self).setdefault("r2r", 5)
    self.vpp()
