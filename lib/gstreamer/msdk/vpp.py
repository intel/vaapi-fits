###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from .util import *

@slash.requires(have_gst)
@slash.requires(*have_gst_element("msdk"))
@slash.requires(*have_gst_element("msdkvpp"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
class VppTest(slash.Test):
  def before(self):
    self.refctx = []

  def gen_input_opts(self):
    if self.vpp_element not in ["deinterlace"]:
      opts = "filesrc location={source} num-buffers={frames}"
      opts += " ! rawvideoparse format={mformat} width={width} height={height}"
    else:
      opts = "filesrc location={source}"
      opts += " ! {gstdecoder}"

    if self.vpp_element not in ["csc", "deinterlace"]:
      if self.ifmt != self.ihwformat:
        opts += " ! videoconvert chroma-mode=none dither=0 ! video/x-raw,format={ihwformat}"

    return opts

  def gen_output_opts(self):
    opts = "msdkvpp hardware=true"
    if self.vpp_element not in ["csc"]:
      if self.vpp_element in ["scale"]:
        opts += " scaling-mode=1"
      elif self.vpp_element in ["deinterlace"]:
        opts += " deinterlace-mode=1 deinterlace-method={mmethod}"
      elif self.vpp_element in ["brightness"]:
        opts += " brightness={mlevel}"
      elif self.vpp_element in ["contrast"]:
        opts += " contrast={mlevel}"
      elif self.vpp_element in ["denoise"]:
        opts += " denoise={level}"
      elif  self.vpp_element in ["hue"]:
        opts += " hue={mlevel}"
      elif  self.vpp_element in ["saturation"]:
        opts += " saturation={mlevel}"
      elif  self.vpp_element in ["sharpen"]:
        opts += " detail={level}"
      elif  self.vpp_element in ["transpose"]:
        opts += " video-direction={direction}"
      elif self.vpp_element in ["crop"]:
        opts += " crop-left={left} crop-right={right} crop-top={top} crop-bottom={bottom}"

      opts += " ! video/x-raw,format={ohwformat}"
      if self.vpp_element in ["scale"]:
        opts += ",width={scale_width},height={scale_height}"
      elif self.vpp_element in ["deinterlace"]:
        opts += ",width={width},height={height}"

      if self.ofmt != self.ohwformat:
        opts += " ! videoconvert chroma-mode=none dither=0 ! video/x-raw,format={mformatu}"
    else:
      opts += " ! video/x-raw,format={ohwformat}"

    opts += " ! checksumsink2 file-checksum=false qos=false frame-checksum=false"
    opts += " plane-checksum=false dump-output=true dump-location={ofile} eos-after={frames}"

    return opts

  def gen_name(self):
    name = "{case}"

    if self.vpp_element in ["scale"]:
      name += "_{scale_width}x{scale_height}"
    elif self.vpp_element in ["crop"]:
      name += "_{crop_width}x{crop_height}"
    else:
      name += "_{width}x{height}"

    if self.vpp_element in ["contrast"]:
      name += "_contrast_{level}"
    elif self.vpp_element in ["saturation"]:
      name += "_saturation_{level}"
    elif self.vpp_element in ["hue"]:
      name += "_hue_{level}"
    elif self.vpp_element in ["brightness"]:
      name += "_brightness_{level}"
    elif self.vpp_element in ["denoise"]:
      name += "_denoise_{level}"
    elif self.vpp_element in ["sharpen"]:
      name += "_sharpen_{level}"
    elif self.vpp_element in ["scale"]:
      name += "_scaled"
    elif self.vpp_element in ["csc"]:
      name += "_csc_{csc}"
    elif self.vpp_element in ["deinterlace"]:
      name += "_deinterlace_{method}_{rate}"
    elif  self.vpp_element in ["transpose"]:
      name += "_transpose_{degrees}_{method}"
    elif self.vpp_element in ["crop"]:
      name += "_crop_{left}_{right}_{top}_{bottom}"

    if vars(self).get("r2r", None) is not None:
      name += "_r2r"

    name += "_{format}"

    return name

  @timefn("gst")
  def call_gst(self, iopts, oopts):
    call("gst-launch-1.0 -vf {iopts} ! {oopts}".format(iopts = iopts, oopts = oopts))

  def validate_caps(self):
    ifmts         = self.caps.get("ifmts", [])
    ofmts         = self.caps.get("ofmts", [])
    self.ifmt     = self.format
    self.ofmt     = self.format if "csc" != self.vpp_element else self.csc
    self.mformat  = mapformat(self.format)
    self.mformatu = mapformatu(self.format)

    # MSDK does not support I420 output formats even though
    # iHD supports it.  Thus, msdkvpp can't output it directly (HW).
    ofmts = list(set(ofmts) - set(["I420"]))

    if self.mformat is None:
      slash.skip_test("gst.{format} unsupported".format(**vars(self)))

    if self.vpp_element in ["csc"]:
      self.ihwformat = mapformatu(self.ifmt if self.ifmt in ifmts else None)
      self.ohwformat = mapformatu(self.ofmt if self.ofmt in ofmts else None)
    else:
      self.ihwformat = map_best_hw_format(self.ifmt, ifmts)
      self.ohwformat = map_best_hw_format(self.ofmt, ofmts)

    if self.ihwformat is None:
      slash.skip_test("{ifmt} unsupported".format(**vars(self)))
    if self.ohwformat is None:
      slash.skip_test("{ofmt} unsupported".format(**vars(self)))

  def vpp(self):
    self.validate_caps()
    iopts = self.gen_input_opts()
    oopts = self.gen_output_opts()
    name  = self.gen_name().format(**vars(self))

    self.ofile = get_media()._test_artifact("{}.yuv".format(name))
    self.call_gst(iopts.format(**vars(self)), oopts.format(**vars(self)))

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = md5(self.ofile)
      get_media()._set_test_details(md5_ref = md5ref)

      for i in range(1, self.r2r):
        self.ofile = get_media()._test_artifact(
          "{}_{}.yuv".format(name, i))
        self.call_gst(iopts.format(**vars(self)), oopts.format(**vars(self)))
        result = md5(self.ofile)
        get_media()._set_test_details(**{ "md5_{:03}".format(i) : result})
        assert result == md5ref, "r2r md5 mismatch"
        #delete output file after each iteration
        get_media()._purge_test_artifact(self.ofile)
    else:
      self.check_metrics()
