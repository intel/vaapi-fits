###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapipostproc"))
@slash.requires(*have_gst_element("checksumsink2"))
class VppTest(slash.Test):
  def before(self):
    self.refctx = []

  def gen_input_opts(self):
    if self.vpp_element not in ["deinterlace"]:
      opts =  "filesrc location={source} num-buffers={frames}"
      opts += " ! rawvideoparse format={mformat} width={width} height={height}"
    else:
      opts =  "filesrc location={source}"
      opts += " ! {gstdecoder}"
    if self.vpp_element not in ["csc", "deinterlace"]:
      opts += " ! videoconvert ! video/x-raw,format={hwup_format}"

    return opts

  def gen_output_opts(self):
    opts = "vaapipostproc"
    if self.vpp_element not in ["csc"]:
      if self.vpp_element not in ["deinterlace"]:
        opts += " format={mformat}"
      if self.vpp_element in ["scale"]:
        opts += " width={scale_width} height={scale_height}"
      else:
        opts += " width={width} height={height}"

      if self.vpp_element in ["contrast"]:
        opts += " contrast={mlevel}"
      elif self.vpp_element in ["saturation"]:
        opts += " saturation={mlevel}"
      elif self.vpp_element in ["hue"]:
        opts += " hue={mlevel}"
      elif self.vpp_element in ["brightness"]:
        opts += " brightness={mlevel}"
      elif self.vpp_element in ["denoise"]:
        opts += " denoise={mlevel}"
      elif self.vpp_element in ["sharpen"]:
        opts += " sharpen={mlevel}"
      elif self.vpp_element in ["deinterlace"]:
        opts += " deinterlace-mode=1 deinterlace-method={mmethod}"
      elif self.vpp_element in ["mirroring"]:
        opts += " video-direction={mmethod}"
    else:
        opts += " ! video/x-raw,format={mcscu}"

    if self.vpp_element in ["deinterlace"]:
      opts += " ! videoconvert ! video/x-raw,format={mformatu}"
    opts += " ! checksumsink2 file-checksum=false qos=false frame-checksum=false"
    opts += " plane-checksum=false dump-output=true dump-location={ofile}"

    return opts

  def gen_name(self):
    name = "{case}"

    if self.vpp_element in ["scale"]:
      name += "_{scale_width}x{scale_height}"
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
    elif self.vpp_element in ["mirroring"]:
      name += "_mirroring_{method}"

    if vars(self).get("r2r", None) is not None:
      name += "_r2r"

    name += "_{format}"

    return name

  @timefn("gst")
  def call_gst(self, iopts, oopts):
    call("gst-launch-1.0 -vf {iopts} ! {oopts}".format(
      iopts = iopts, oopts = oopts))

  def vpp(self):
    self.mformat     = mapformat(self.format)
    self.hwup_format = mapformat_hwup(self.format)
    iopts            = self.gen_input_opts()
    oopts            = self.gen_output_opts()
    name             = self.gen_name().format(**vars(self))

    self.ofile = get_media()._test_artifact("{}.yuv".format(name))
    self.call_gst(iopts.format(**vars(self)), oopts.format(**vars(self)))

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = md5(self.ofile)
      get_media()._set_test_details(md5_ref = md5ref)

      for i in xrange(1, self.r2r):
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
