###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash

from ...lib.common import timefn, get_media, call, exe2os, filepath2os
from ...lib.gstreamer.util import have_gst, have_gst_element
from ...lib.mixin.vpp import VppMetricMixin

from ...lib import metrics2

@slash.requires(have_gst)
@slash.requires(*have_gst_element("checksumsink2"))
class BaseVppTest(slash.Test, VppMetricMixin):
  def before(self):
    self.refctx = []
    self.post_validate = lambda: None

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
      opts = "filesrc location={ossource} num-buffers={frames}"
      opts += " ! rawvideoparse format={mformat} width={width} height={height}"
    else:
      opts =  "filesrc location={ossource}"
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
    opts += " plane-checksum=false dump-output=true dump-location={osdecoded} eos-after={frames}"

    return opts

  @timefn("gst:vpp")
  def call_gst(self, iopts, oopts):
    if vars(self).get("decoded", None) is not None:
      get_media()._purge_test_artifact(self.decoded)
    self.decoded = get_media()._test_artifact2("yuv")
    self.osdecoded = filepath2os(self.decoded)

    iopts = iopts.format(**vars(self))
    oopts = oopts.format(**vars(self))

    call(f"{exe2os('gst-launch-1.0')} -vf {iopts} ! {oopts}")

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

    self.post_validate()

  def vpp(self):
    self.validate_caps()

    iopts = self.gen_input_opts()
    oopts = self.gen_output_opts()
    self.ossource = filepath2os(self.source)

    self.call_gst(iopts, oopts)

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"

      metric = metrics2.factory.create(metric = dict(type = "md5", numbytes = -1))
      metric.update(filetest = self.decoded)
      metric.expect = metric.actual # the first run is our reference for r2r
      metric.check()

      for i in range(1, self.r2r):
        self.call_gst(iopts, oopts)
        metric.update(filetest = self.decoded)
        metric.check()
    else:
      self.check_metrics()
