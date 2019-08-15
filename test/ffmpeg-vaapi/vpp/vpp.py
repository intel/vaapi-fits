###
### Copyright (C) 2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
class VppTest(slash.Test):
  def before(self):
    self.refctx = []

  def gen_input_opts(self):
    if self.vpp_op not in ["deinterlace"]:
      opts = "-f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    else:
      opts = "-c:v {ffdecoder}"
    opts += " -i {source}"

    return opts

  def gen_output_opts(self):
    vfilter = []
    if self.vpp_op not in ["csc"]:
      vfilter.append("format={hwformat}|vaapi")
    vfilter.append("hwupload")
    vfilter.append(
      dict(
        brightness  = "procamp_vaapi=b={mlevel}",
        contrast    = "procamp_vaapi=c={mlevel}",
        hue         = "procamp_vaapi=h={mlevel}",
        saturation  = "procamp_vaapi=s={mlevel}",
        denoise     = "denoise_vaapi=denoise={mlevel}",
        scale       = "scale_vaapi=w={scale_width}:h={scale_height}",
        sharpen     = "sharpness_vaapi=sharpness={mlevel}",
        deinterlace = "deinterlace_vaapi=mode={mmethod}:rate={rate}",
        csc         = "scale_vaapi=format={hwformat}",
        transpose   = "transpose_vaapi=dir={direction}",
      )[self.vpp_op]
    )
    vfilter.append("hwdownload")
    vfilter.append("format={hwformat}")

    opts  = "-vf '{}'".format(",".join(vfilter))
    if self.vpp_op not in ["csc"]:
      opts += " -pix_fmt {mformat}"
    opts += " -f rawvideo -vsync passthrough -an -vframes {frames} -y {decoded}"

    return opts

  def gen_name(self):
    name = "{case}_{vpp_op}"
    name += dict(
      brightness  = "_{level}_{width}x{height}_{format}",
      contrast    = "_{level}_{width}x{height}_{format}",
      hue         = "_{level}_{width}x{height}_{format}",
      saturation  = "_{level}_{width}x{height}_{format}",
      denoise     = "_{level}_{width}x{height}_{format}",
      scale       = "_{scale_width}x{scale_height}_{format}",
      sharpen     = "_{level}_{width}x{height}_{format}",
      deinterlace = "_{method}_{rate}_{width}x{height}_{format}",
      csc         = "_{width}x{height}_{format}_to_{csc}",
      transpose   = "_{degrees}_{method}_{width}x{height}_{format}",
    )[self.vpp_op]

    if vars(self).get("r2r", None) is not None:
      name += "_r2r"

    return name

  @timefn("ffmpeg")
  def call_ffmpeg(self, iopts, oopts):
    call(
      "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
      " {iopts} {oopts}".format(iopts = iopts, oopts = oopts))

  def vpp(self):
    if self.vpp_op not in ["csc"]:
      self.hwformat = maphwformat(self.format)
    else:
      self.hwformat = mapformat(self.csc)
      if self.hwformat is None:
        slash.skip_test("{csc} format not supported".format(**vars(self)))

    self.mformat  = mapformat(self.format)
    iopts         = self.gen_input_opts()
    oopts         = self.gen_output_opts()
    name          = self.gen_name().format(**vars(self))

    if self.mformat is None:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    self.decoded = get_media()._test_artifact("{}.yuv".format(name))
    self.call_ffmpeg(iopts.format(**vars(self)), oopts.format(**vars(self)))

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = md5(self.decoded)
      get_media()._set_test_details(md5_ref = md5ref)

      for i in xrange(1, self.r2r):
        self.decoded = get_media()._test_artifact("{}_{}.yuv".format(name, i))
        self.call_ffmpeg(iopts.format(**vars(self)), oopts.format(**vars(self)))
        result = md5(self.decoded)
        get_media()._set_test_details(**{ "md5_{:03}".format(i) : result})
        assert result == md5ref, "r2r md5 mismatch"
        #delete output file after each iteration
        get_media()._purge_test_artifact(self.decoded)
    else:
      self.check_metrics()
