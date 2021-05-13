###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.vpp import VppTest

if len(load_test_spec("vpp", "deinterlace")):
  slash.logger.warn(
    "gst-vaapi: vpp deinterlace with raw input is no longer supported")

@slash.requires(*platform.have_caps("vpp", "deinterlace"))
class DeinterlaceTest(VppTest):
  _default_methods_ = [
    "bob",
    "weave",
    "motion-adaptive",
    "motion-compensated",
  ]

  _default_modes_ = [
    dict(method = m, rate = "field") for m in _default_methods_
  ]

  def before(self):
    vars(self).update(
      metric      = dict(type = "md5"), # default metric
      vpp_element = "deinterlace",
    )
    super(DeinterlaceTest, self).before()

  def init(self, tspec, case, method, rate):
    vars(self).update(tspec[case].copy())
    vars(self).update(case = case, method = method, rate = rate)

    self.gstdecoder = self.gstdecoder.format(**vars(self))
    self.frames *= 2 # field rate produces double number of frames

  def validate_caps(self):
    self.caps = platform.get_caps(
      "vpp", "deinterlace", self.method.replace('-', '_'))

    if self.caps is None:
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{method} not supported", **vars(self)))

    # The rate is fixed in vaapipostproc deinterlace.  It always outputs at
    # field rate (one frame of output for each field).
    if "field" != self.rate:
      slash.skip_test("{rate} rate not supported".format(**vars(self)))

    self.mmethod = map_deinterlace_method(self.method)
    if self.mmethod is None:
      slash.skip_test("{method} not supported".format(**vars(self)))

    super(DeinterlaceTest, self).validate_caps()

  def check_metrics(self):
    if vars(self).get("reference", None) is not None:
      self.reference = format_value(self.reference, **vars(self))
    check_metric(decoded = self.ofile, **vars(self))

spec_avc      = load_test_spec("vpp", "deinterlace", "avc")
spec_avc_r2r  = load_test_spec("vpp", "deinterlace", "avc", "r2r")
@slash.requires(*platform.have_caps("decode", "avc"))
@slash.requires(*have_gst_element("vaapih264dec"))
class avc(DeinterlaceTest):
  def before(self):
    self.gstdecoder = "h264parse ! vaapih264dec"
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
@slash.requires(*have_gst_element("vaapimpeg2dec"))
class mpeg2(DeinterlaceTest):
  def before(self):
    self.gstdecoder = "mpegvideoparse ! vaapimpeg2dec"
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
@slash.requires(*have_gst_element("vaapivc1dec"))
class vc1(DeinterlaceTest):
  def before(self):
    self.gstdecoder  = "'video/x-wmv,profile=(string)advanced',width={width}"
    self.gstdecoder += ",height={height},framerate=14/1 ! vaapivc1dec"
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
