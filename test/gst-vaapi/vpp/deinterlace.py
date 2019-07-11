###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .vpp import VppTest

if len(load_test_spec("vpp", "deinterlace")):
  slash.logger.warn(
    "gst-vaapi: vpp deinterlace with raw input is no longer supported")

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
    # default metric
    self.metric = dict(type = "md5")
    vars(self).update(
      vpp_element = "deinterlace"
    )
    super(DeinterlaceTest, self).before()


  def init(self, tspec, case, method, rate):
    vars(self).update(tspec[case].copy())
    vars(self).update(case = case, method = method, rate = rate)

  def deinterlace(self):
    self.mmethod  = map_deinterlace_method(self.method)
    self.gstdecoder = self.gstdecoder.format(**vars(self))
    # field rate produces double number of frames
    self.frames *= 2

    # The rate is fixed in vaapipostproc deinterlace.  It always outputs at
    # field rate (one frame of output for each field).
    if "field" != self.rate:
      slash.skip_test("{rate} rate not supported".format(**vars(self)))

    if self.mmethod is None:
      slash.skip_test("{method} method not supported".format(**vars(self)))

    self.vpp()

  def check_metrics(self):
    if vars(self).get("reference", None) is not None:
      self.reference = format_value(self.reference, **vars(self))
    check_metric(decoded = self.ofile, **vars(self))

spec_avc = load_test_spec("vpp", "deinterlace", "avc")
spec_avc_r2r = load_test_spec("vpp", "deinterlace", "avc", "r2r")
class avc(DeinterlaceTest):
  def before(self):
    self.gstdecoder = "h264parse ! vaapih264dec"
    super(avc, self).before()

  @platform_tags(set(AVC_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_gst_element("vaapih264dec"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_avc, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    self.init(spec_avc, case, method, rate)
    self.deinterlace()

  @platform_tags(set(AVC_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_gst_element("vaapih264dec"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_avc_r2r, DeinterlaceTest._default_modes_))
  def test_r2r(self, case, method, rate):
    self.init(spec_avc_r2r, case, method, rate)
    vars(self).setdefault("r2r", 5)
    self.deinterlace()

spec_mpeg2 = load_test_spec("vpp", "deinterlace", "mpeg2")
spec_mpeg2_r2r = load_test_spec("vpp", "deinterlace", "mpeg2", "r2r")
class mpeg2(DeinterlaceTest):
  def before(self):
    self.gstdecoder = "mpegvideoparse ! vaapimpeg2dec"
    super(mpeg2, self).before()

  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_gst_element("vaapimpeg2dec"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_mpeg2, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    self.init(spec_mpeg2, case, method, rate)
    self.deinterlace()

  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_gst_element("vaapimpeg2dec"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_mpeg2_r2r, DeinterlaceTest._default_modes_))
  def test_r2r(self, case, method, rate):
    self.init(spec_mpeg2_r2r, case, method, rate)
    vars(self).setdefault("r2r", 5)
    self.deinterlace()

spec_vc1 = load_test_spec("vpp", "deinterlace", "vc1")
spec_vc1_r2r = load_test_spec("vpp", "deinterlace", "vc1", "r2r")
class vc1(DeinterlaceTest):
  def before(self):
    self.gstdecoder  = "'video/x-wmv,profile=(string)advanced',width={width}"
    self.gstdecoder += ",height={height},framerate=14/1 ! vaapivc1dec"
    super(vc1, self).before()

  @platform_tags(set(VC1_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_gst_element("vaapivc1dec"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_vc1, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    self.init(spec_vc1, case, method, rate)
    self.deinterlace()

  @platform_tags(set(VC1_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_gst_element("vaapivc1dec"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_vc1_r2r, DeinterlaceTest._default_modes_))
  def test_r2r(self, case, method, rate):
    self.init(spec_vc1_r2r, case, method, rate)
    vars(self).setdefault("r2r", 5)
    self.deinterlace()
