###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib import platform, format_value
from ....lib.codecs import Codec
from ....lib.gstreamer.vppbase import BaseVppTest
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.va.util import map_best_hw_format, mapformat, mapformatu, map_deinterlace_method
from ....lib.common import get_media, mapRange, mapRangeWithDefault

@slash.requires(*have_gst_element("va"))
class VppTest(BaseVppTest):
  def map_best_hw_format(self, format, hwformats):
    return map_best_hw_format(format, hwformats)

  def map_format(self, format):
    return mapformat(format)

  def map_formatu(self, format):
    return mapformatu(format)

  def gen_vpp_opts(self):
    opts = ""

    procamp = dict(
      brightness  = [-100.0,   0.0, 100.0],
      contrast    = [   0.0,   1.0,  10.0],
      hue         = [-180.0,   0.0, 180.0],
      saturation  = [   0.0,   1.0,  10.0],
    )

    if self.vpp_op in procamp:
      self.mlevel = mapRangeWithDefault(
        self.level, [0.0, 50.0, 100.0], procamp[self.vpp_op]
      )
      opts += " {vpp_op}={mlevel}"
    elif self.vpp_op in ["denoise"]:
      oprange = dict(
        i965 = [0.0, 1.0],
      ).get(get_media()._get_driver_name(), [0.0, 64.0])
      self.mlevel = mapRange(self.level, [0, 100], oprange)
      opts += " {vpp_op}={mlevel}"
    elif self.vpp_op in ["sharpen"]:
      self.mlevel = mapRangeWithDefault(
        self.level, [0.0, 50.0, 100.0], [0.0, 44.0, 64.0]
      )
      opts += " {vpp_op}={mlevel}"
    elif self.vpp_op in ["transpose"]:
      opts += " video-direction={direction}"
    elif self.vpp_op in ["crop"]:
      opts += " disable-passthrough=true"
    elif self.vpp_op in ["composite"]:
      opts += " name=composite"
      for n, comp in enumerate(self.comps):
        opts += (
          " sink_{n}::xpos={x}"
          " sink_{n}::ypos={y}"
          " sink_{n}::alpha={a}"
          "".format(n = n, **comp)
        )
    elif self.vpp_op in ["deinterlace"]:
      opts += " method={mmethod}"
    return opts

  def gen_input_opts(self):
    opts = super().gen_input_opts()
    if self.vpp_op in ["composite"]:
      opts += " ! tee name=source ! queue"
    elif self.vpp_op in ["crop"]:
      opts += " ! videocrop left={left} right={right} top={top} bottom={bottom}"
    return opts

  def gen_output_opts(self):
    opts = super().gen_output_opts()
    if self.vpp_op in ["composite"]:
      # The first composition is piped directly to vacompositor.
      # Pipe the rest of them here.
      opts += " source. ! queue ! composite. " * int(len(self.comps) - 1)
    return opts

def vpp_test_class(op):
  hwdevice = get_media().render_device.split('/')[-1]
  hw = hwdevice if hwdevice not in ['renderD128', '0'] else ""

  gstvpp = {
    "composite"   : f"va{hw}compositor",
    "deinterlace" : f"va{hw}deinterlace",
  }.get(op, f"va{hw}postproc")

  @slash.requires(*have_gst_element(gstvpp))
  @slash.requires(*platform.have_caps("vpp", op))
  class VppTestClass(VppTest):
    def before(self):
      super().before()
      vars(self).update(
        caps    = platform.get_caps("vpp", op),
        gstvpp  = gstvpp,
        vpp_op  = op,
      )

  return VppTestClass

def deinterlace_test_class(codec):
  # gst element codec translation
  gstcodec = {
    Codec.AVC   : "h264",
  }.get(codec, codec)

  gstparser = {
    Codec.MPEG2 : "mpegvideoparse",
  }.get(codec, f"{gstcodec}parse")

  hwdevice = get_media().render_device.split('/')[-1]
  hw = hwdevice if hwdevice not in ['renderD128', '0'] else ""

  @slash.requires(*have_gst_element(f"va{hw}{gstcodec}dec"))
  @slash.requires(*platform.have_caps("decode", codec))
  class DeinterlaceTestClass(vpp_test_class("deinterlace")):
    _default_methods_ = [
      "bob",
      "motion-adaptive",
      "motion-compensated",
    ]

    _default_modes_ = [
      dict(method = m, rate = "field") for m in _default_methods_
    ]

    def before(self):
      super().before()
      vars(self).update(
        metric      = dict(type = "md5"),
        gstdecoder  = f"{gstparser} ! va{hw}{gstcodec}dec",
      )

    def init(self, tspec, case, method, rate):
      vars(self).update(tspec[case].copy())
      vars(self).update(case = case, method = method, rate = rate)

      self.frames *= 2 # field rate produces double number of frames

    def validate_caps(self):
      self.caps = platform.get_caps(
        "vpp", "deinterlace", self.method.replace('-', '_'))

      if self.caps is None:
        slash.skip_test(
          format_value(
            "{platform}.{driver}.{method} not supported", **vars(self)))

      # The rate is fixed in vadeinterlace.  It always outputs at
      # field rate (one frame of output for each field).
      if "field" != self.rate:
        slash.skip_test("{rate} rate not supported".format(**vars(self)))

      self.mmethod = map_deinterlace_method(self.method)
      if self.mmethod is None:
        slash.skip_test("{method} not supported".format(**vars(self)))

      super().validate_caps()

  return DeinterlaceTestClass

VppBrightnessTest   = vpp_test_class("brightness")
VppContrastTest     = vpp_test_class("contrast")
VppHueTest          = vpp_test_class("hue")
VppSaturationTest   = vpp_test_class("saturation")
VppCompositeTest    = vpp_test_class("composite")
VppCropTest         = vpp_test_class("crop")
VppCscTest          = vpp_test_class("csc")
VppDenoiseTest      = vpp_test_class("denoise")
VppTransposeTest    = vpp_test_class("transpose")
VppScaleTest        = vpp_test_class("scale")
VppSharpenTest      = vpp_test_class("sharpen")

VppAVCDeinterlaceTest   = deinterlace_test_class(Codec.AVC)
VppMPEG2DeinterlaceTest = deinterlace_test_class(Codec.MPEG2)
