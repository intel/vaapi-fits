###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash

from ...lib.common import timefn, get_media, call
from ...lib.gstreamer.util import have_gst, have_gst_element
from ...lib.metrics import md5
from ...lib.mixin.vpp import VppMetricMixin

@slash.requires(have_gst)
@slash.requires(*have_gst_element("checksumsink2"))
class BaseVppTest(slash.Test, VppMetricMixin):
  def before(self):
    self.refctx = []

  def get_input_formats(self):
    return self.caps.get("ifmts", [])

  def get_output_formats(self):
    return self.caps.get("ofmts", [])

  def map_best_hw_format(self, format, hwformats):
    raise NotImplementedError

  def map_format(self, format):
    raise NotImplementedError

  def map_formatu(self, format):
    raise NotImplementedError

  def gen_vpp_opts(self):
    raise NotImplementedError

  def gen_input_opts(self):
    if self.vpp_op not in ["deinterlace"]:
      opts =  "filesrc location={source} num-buffers={frames}"
      opts += " ! rawvideoparse format={mformat} width={width} height={height}"
    else:
      opts =  "filesrc location={source}"
      opts += " ! {gstdecoder}"
    if self.vpp_op not in ["csc", "deinterlace"]:
      if self.ifmt != self.ihwformat:
        opts += " ! videoconvert chroma-mode=none dither=0 ! video/x-raw,format={ihwformat}"

    return opts

  def gen_output_opts(self):
    opts = "{gstvpp} " + self.gen_vpp_opts()
    opts += " ! video/x-raw,format={ohwformat}"
    if self.vpp_op in ["scale"]:
      opts += ",width={scale_width},height={scale_height}"
    elif self.vpp_op in ["deinterlace"]:
      opts += ",width={width},height={height}"
    if self.ofmt != self.ohwformat and self.vpp_op not in ["csc"]:
      opts += " ! videoconvert chroma-mode=none dither=0 ! video/x-raw,format={mformatu}"
    opts += " ! checksumsink2 file-checksum=false qos=false frame-checksum=false"
    opts += " plane-checksum=false dump-output=true dump-location={decoded} eos-after={frames}"

    return opts

  def gen_name(self):
    name = "{case}"
    if self.vpp_op in ["scale"]:
      name += "_{scale_width}x{scale_height}"
    elif self.vpp_op in ["crop"]:
      name += "_{crop_width}x{crop_height}"
    else:
      name += "_{width}x{height}"
    if self.vpp_op in ["contrast"]:
      name += "_contrast_{level}"
    elif self.vpp_op in ["saturation"]:
      name += "_saturation_{level}"
    elif self.vpp_op in ["hue"]:
      name += "_hue_{level}"
    elif self.vpp_op in ["brightness"]:
      name += "_brightness_{level}"
    elif self.vpp_op in ["denoise"]:
      name += "_denoise_{level}"
    elif self.vpp_op in ["sharpen"]:
      name += "_sharpen_{level}"
    elif self.vpp_op in ["scale"]:
      name += "_scaled"
    elif self.vpp_op in ["csc"]:
      name += "_csc_{csc}"
    elif self.vpp_op in ["deinterlace"]:
      name += "_deinterlace_{method}_{rate}"
    elif self.vpp_op in ["transpose"]:
      name += "_transpose_{degrees}_{method}"
    elif self.vpp_op in ["crop"]:
      name += "_crop_{left}_{right}_{top}_{bottom}"
    elif self.vpp_op in ["composite"]:
      name += "_composite"
    if vars(self).get("r2r", None) is not None:
      name += "_r2r"
    name += "_{format}"

    return name

  @timefn("gst")
  def call_gst(self, iopts, oopts):
    call("gst-launch-1.0 -vf {iopts} ! {oopts}".format(iopts = iopts, oopts = oopts))

  def validate_caps(self):
    ifmts         = self.get_input_formats()
    ofmts         = self.get_output_formats()
    self.ifmt     = self.format
    self.ofmt     = self.format if "csc" != self.vpp_op else self.csc
    self.mformat  = self.map_format(self.format)
    self.mformatu = self.map_formatu(self.format)

    if self.mformat is None:
      slash.skip_test("{gstvpp}.{format} unsupported".format(**vars(self)))

    if "csc" == self.vpp_op:
      self.ihwformat = self.map_formatu(self.ifmt if self.ifmt in ifmts else None)
      self.ohwformat = self.map_formatu(self.ofmt if self.ofmt in ofmts else None)
    else:
      self.ihwformat = self.map_best_hw_format(self.ifmt, ifmts)
      self.ohwformat = self.map_best_hw_format(self.ofmt, ofmts)

    if self.ihwformat is None:
      slash.skip_test("{ifmt} unsupported".format(**vars(self)))
    if self.ohwformat is None:
      slash.skip_test("{ofmt} unsupported".format(**vars(self)))

  def vpp(self):
    self.validate_caps()

    iopts = self.gen_input_opts()
    oopts = self.gen_output_opts()
    name  = self.gen_name().format(**vars(self))

    self.decoded = get_media()._test_artifact("{}.yuv".format(name))
    self.call_gst(iopts.format(**vars(self)), oopts.format(**vars(self)))

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = md5(self.decoded)
      get_media()._set_test_details(md5_ref = md5ref)

      for i in range(1, self.r2r):
        self.decoded = get_media()._test_artifact(
          "{}_{}.yuv".format(name, i))
        self.call_gst(iopts.format(**vars(self)), oopts.format(**vars(self)))
        result = md5(self.decoded)
        get_media()._set_test_details(**{ "md5_{:03}".format(i) : result})
        assert result == md5ref, "r2r md5 mismatch"
        #delete output file after each iteration
        get_media()._purge_test_artifact(self.decoded)
    else:
      self.check_metrics()
