###
### Copyright (C) 2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash

from ...lib.common import timefn, get_media, call, exe2os, filepath2os
from ...lib.ffmpeg.util import have_ffmpeg, BaseFormatMapper
from ...lib.mixin.vpp import VppMetricMixin

from ...lib import metrics2

@slash.requires(have_ffmpeg)
class BaseVppTest(slash.Test, BaseFormatMapper, VppMetricMixin):
  def before(self):
    self.refctx = []
    self.post_validate = lambda: None
    self.hwdevice = f"hw:{get_media().render_device}"

  def get_input_formats(self):
    return self.caps.get("ifmts", [])

  def get_output_formats(self):
    return self.caps.get("ofmts", [])

  def gen_vpp_opts(self):
    raise NotImplementedError

  def gen_input_opts(self):
    if self.vpp_op in ["deinterlace", "tonemap"]:
      opts = "-c:v {ffdecoder}"
    elif self.vpp_op in ["stack", "overlay", "range"]:
      opts = ""
    else:
      opts = "-f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    opts += " -i {ossource}"

    if self.vpp_op in ["overlay"]:
      opts += " -i {ossource1}"

    return opts

  def gen_output_opts(self):
    fcomplex = ["composite", "stack", "overlay"]
    vpfilter = self.gen_vpp_opts()
    vpfilter.append("hwdownload")
    vpfilter.append("format={ohwformat}")

    opts = "-filter_complex" if self.vpp_op in fcomplex else "-vf"
    opts += f" '{','.join(vpfilter)}'"
    opts += " -pix_fmt {mformat}" if self.vpp_op not in ["csc", "tonemap", "overlay"] else ""
    opts += " -f rawvideo -fps_mode passthrough -an -vframes {frames} -y {osdecoded}"

    return opts

  @timefn("ffmpeg:vpp")
  def call_ffmpeg(self, iopts, oopts):
    if vars(self).get("decoded", None) is not None:
      get_media()._purge_test_artifact(self.decoded)
    self.decoded = get_media()._test_artifact2("yuv")
    self.osdecoded  = filepath2os(self.decoded)

    iopts = iopts.format(**vars(self))
    oopts = oopts.format(**vars(self))

    call(
      f"{exe2os('ffmpeg')} -hwaccel {self.hwaccel}"
      f" -init_hw_device {self.hwaccel}={self.hwdevice}"
      f" -hwaccel_output_format {self.hwaccel}"
      f" -v verbose {iopts} {oopts}"
    )

  def validate_caps(self):
    ifmts         = self.get_input_formats()
    ofmts         = self.get_output_formats()
    self.ifmt     = self.format
    self.ofmt     = self.format if  self.vpp_op not in ["csc", "tonemap"] else self.csc
    self.mformat  = self.map_format(self.format)

    if self.mformat is None:
      slash.skip_test(f"ffmpeg.{self.format} unsupported")

    if self.vpp_op in ["csc", "tonemap"]:
      self.ihwformat = self.map_format(self.ifmt if self.ifmt in ifmts else None)
      self.ohwformat = self.map_format(self.ofmt if self.ofmt in ofmts else None)
    else:
      self.ihwformat = self.map_best_hw_format(self.ifmt, ifmts)
      self.ohwformat = self.map_best_hw_format(self.ofmt, ofmts)

    if self.ihwformat is None:
      slash.skip_test(f"{self.ifmt} unsupported")
    if self.ohwformat is None:
      slash.skip_test(f"{self.ofmt} unsupported")

    if self.vpp_op in ["composite"]:
      self.owidth, self.oheight = self.width, self.height
      for comp in self.comps:
        self.owidth = max(self.owidth, self.width + comp['x'])
        self.oheight = max(self.oheight, self.height + comp['y'])

    self.post_validate()

  def vpp(self):
    self.validate_caps()

    iopts = self.gen_input_opts()
    oopts = self.gen_output_opts()
    self.ossource = filepath2os(self.source)

    if self.vpp_op in ["overlay"]:
      self.ossource1 = filepath2os(self.source1)

    self.call_ffmpeg(iopts, oopts)

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"

      metric = metrics2.factory.create(metric = dict(type = "md5", numbytes = -1))
      metric.update(filetest = self.decoded)
      metric.expect = metric.actual # the first run is our reference for r2r
      metric.check()

      for i in range(1, self.r2r):
        self.call_ffmpeg(iopts, oopts)
        metric.update(filetest = self.decoded)
        metric.check()
    else:
      self.check_metrics()
