###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

if len(load_test_spec("vpp", "deinterlace")):
  slash.logger.warn(
    "gst-msdk: vpp deinterlace with raw input is no longer supported")

@slash.requires(have_gst)
@slash.requires(*have_gst_element("msdk"))
@slash.requires(*have_gst_element("msdkvpp"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
class DeinterlaceTest(slash.Test):
  _default_methods_ = [
    "bob",
    "advanced",
    "advanced-no-ref",
    "advanced-scd",
    "weave",
  ]

  _default_modes_ = [
    dict(method = m, rate = "frame") for m in _default_methods_
  ]

  def before(self):
    # default metric
    self.metric = dict(type = "md5")
    self.refctx = []

  @timefn("gst")
  def call_gst(self):
    call(
      "gst-launch-1.0 -vf filesrc location={source} ! {gstdecoder}"
      " ! msdkvpp hardware=true deinterlace-mode=1 deinterlace-method={mmethod}"
      " ! video/x-raw,format=NV12,width={width},height={height}"
      " ! videoconvert ! video/x-raw,format={mformatu}"
      " ! checksumsink2 file-checksum=false qos=false frame-checksum=false"
      " plane-checksum=false dump-output=true dump-location={decoded}"
      "".format(**vars(self)))

  def get_name_tmpl(self):
    return "{case}_di_{method}_{rate}_{width}x{height}_{format}"

  def deinterlace(self):
    self.mformatu = mapformatu(self.format)
    self.mmethod  = map_deinterlace_method(self.method)

    # The rate is fixed in msdkvpp deinterlace.  It always outputs at
    # frame rate (one frame of output for each field-pair).
    if "frame" != self.rate:
      slash.skip_test("{rate} rate not supported".format(**vars(self)))

    if self.mformatu is None:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    if self.mmethod is None:
      slash.skip_test("{method} method not supported".format(**vars(self)))

    name = self.get_name_tmpl().format(**vars(self))
    self.decoded = get_media()._test_artifact("{}.raw".format(name))
    self.gstdecoder = self.gstdecoder.format(**vars(self))
    self.call_gst()
    self.check_metrics()

  def check_metrics(self):
    if vars(self).get("reference", None) is not None:
      self.reference = format_value(self.reference, **vars(self))
    check_metric(**vars(self))

spec_avc = load_test_spec("vpp", "deinterlace", "avc")
class avc(DeinterlaceTest):
  def before(self):
    self.gstdecoder = "h264parse ! msdkh264dec"
    super(avc, self).before()

  @platform_tags(set(AVC_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_gst_element("msdkh264dec"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_avc, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    vars(self).update(spec_avc[case].copy())
    vars(self).update(case = case, method = method, rate = rate)
    self.deinterlace()

spec_mpeg2 = load_test_spec("vpp", "deinterlace", "mpeg2")
class mpeg2(DeinterlaceTest):
  def before(self):
    self.gstdecoder = "mpegvideoparse ! msdkmpeg2dec"
    super(mpeg2, self).before()

  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_gst_element("msdkmpeg2dec"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_mpeg2, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    vars(self).update(spec_mpeg2[case].copy())
    vars(self).update(case = case, method = method, rate = rate)
    self.deinterlace()

spec_vc1 = load_test_spec("vpp", "deinterlace", "vc1")
class vc1(DeinterlaceTest):
  def before(self):
    self.gstdecoder  = "'video/x-wmv,profile=(string)advanced',width={width}"
    self.gstdecoder += ",height={height},framerate=14/1 ! msdkvc1dec"
    super(vc1, self).before()

  @platform_tags(set(VC1_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_gst_element("msdkvc1dec"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_vc1, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    vars(self).update(spec_vc1[case].copy())
    vars(self).update(case = case, method = method, rate = rate)
    self.deinterlace()
