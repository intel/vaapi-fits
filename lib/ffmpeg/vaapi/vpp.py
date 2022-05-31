###
### Copyright (C) 2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from .util import *

@slash.requires(have_ffmpeg)
@slash.requires(*have_ffmpeg_hwaccel("vaapi"))
class VppTest(slash.Test, BaseFormatMapper):
  def before(self):
    self.refctx = []
    self.renderDevice = get_media().render_device
    self.post_validate = lambda: None

  def gen_input_opts(self):
    opts = ""  
    if self.vpp_op not in ["deinterlace", "scale_qsv", "scale_vulkan"]:
      opts += "-f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    elif self.vpp_op in ["deinterlace"]:
      opts += "-c:v {ffdecoder}"
    else:
      opts += "-hwaccel_output_format vaapi"
    opts += " -i {source}"

    return opts

  def gen_output_opts(self):
    vfilter = []
    if self.vpp_op in ["composite"]:
      opts = "-filter_complex"

      vfilter.append("color=black:size={owidth}x{oheight}")
      vfilter.append("format={ihwformat}|vaapi")
      vfilter.append("hwupload")

      for n, comp in enumerate(self.comps):
        vfilter[-1] += "[out{n}];[0:v]format={ihwformat}|vaapi".format(n = n, **vars(self))
        vfilter.append(
          "hwupload[in{n}];[out{n}][in{n}]overlay_vaapi=x={x}:y={y}:alpha={a}"
          "".format(n = n, **comp)
        )
    else:
      opts = "-vf"

      if self.vpp_op not in ["csc", "scale_qsv", "scale_vulkan"]:
        vfilter.append("format={ihwformat}|vaapi")
      
      if self.vpp_op not in ["scale_qsv", "scale_vulkan"]:
        vfilter.append("hwupload")
      elif self.vpp_op in ["scale_qsv"]:
        # self.vpp_op == "scale_qsv"
        vfilter.append("hwmap=derive_device=qsv,format=qsv")
      else:
        # self.vpp_op == "scale_vulkan"
        vfilter.append("hwmap=derive_device=vulkan,format=vulkan")


      vfilter.append(
        dict(
          brightness  = "procamp_vaapi=b={mlevel}",
          contrast    = "procamp_vaapi=c={mlevel}",
          hue         = "procamp_vaapi=h={mlevel}",
          saturation  = "procamp_vaapi=s={mlevel}",
          denoise     = "denoise_vaapi=denoise={mlevel}",
          scale       = "scale_vaapi=w={scale_width}:h={scale_height}",
          scale_qsv   = "vpp_qsv=w={scale_width}:h={scale_height}",
          scale_vulkan= "scale_vulkan=w={scale_width}:h={scale_height}",
          sharpen     = "sharpness_vaapi=sharpness={mlevel}",
          deinterlace = "deinterlace_vaapi=mode={mmethod}:rate={rate}",
          csc         = "scale_vaapi=format={ohwformat}",
          transpose   = "transpose_vaapi=dir={direction}",
        )[self.vpp_op]
      )

    if vars(self).get("encoder", None) is not None:
      if "scale_qsv" != self.vpp_op or "h264_qsv" != self.encoder:
        if "scale_qsv" == self.vpp_op and "h264_vaapi" == self.encoder:
          vfilter.append("hwmap=derive_device=vaapi,format=vaapi")
        elif "scale_vulkan" == self.vpp_op:
          vfilter.append("hwmap=derive_device=vaapi,format=vaapi")
          if "h264_qsv" == self.encoder:
            vfilter.append("hwmap=derive_device=qsv,format=qsv")
          
      opts += " '{}'".format(",".join(vfilter))
      opts += " -c:v {encoder} -vframes {frames} -y {encoded}"
    else:
      vfilter.append("hwdownload")
      vfilter.append("format={ohwformat}")

      opts += " '{}'".format(",".join(vfilter))
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
      scale_qsv   = "_{scale_width}x{scale_height}_{format}_{encoder}",
      scale_vulkan= "_{scale_width}x{scale_height}_{format}_{encoder}",
      sharpen     = "_{level}_{width}x{height}_{format}",
      deinterlace = "_{method}_{rate}_{width}x{height}_{format}",
      csc         = "_{width}x{height}_{format}_to_{csc}",
      transpose   = "_{degrees}_{method}_{width}x{height}_{format}",
      composite   = "_{owidth}x{oheight}_{format}",
    )[self.vpp_op]

    if vars(self).get("r2r", None) is not None:
      name += "_r2r"

    return name

  @timefn("ffmpeg")
  def call_ffmpeg(self, iopts, oopts):
    call(
      "ffmpeg -hwaccel vaapi -vaapi_device {renderDevice} -v verbose"
      " {iopts} {oopts}".format(renderDevice = self.renderDevice, iopts = iopts, oopts = oopts))

  def validate_caps(self):
    ifmts         = self.caps.get("ifmts", [])
    ofmts         = self.caps.get("ofmts", [])
    self.ifmt     = self.format
    self.ofmt     = self.format if "csc" != self.vpp_op else self.csc
    self.mformat  = self.map_format(self.format)

    if self.mformat is None:
      slash.skip_test("ffmpeg.{format} unsupported".format(**vars(self)))

    if self.vpp_op in ["csc"]:
      self.ihwformat = self.map_format(self.ifmt if self.ifmt in ifmts else None)
      self.ohwformat = self.map_format(self.ofmt if self.ofmt in ofmts else None)
    else:
      self.ihwformat = self.map_best_hw_format(self.ifmt, ifmts)
      self.ohwformat = self.map_best_hw_format(self.ofmt, ofmts)

    if self.ihwformat is None:
      slash.skip_test("{ifmt} unsupported".format(**vars(self)))
    if self.ohwformat is None:
      slash.skip_test("{ofmt} unsupported".format(**vars(self)))

    if self.vpp_op in ["composite"]:
      self.owidth, self.oheight = self.width, self.height
      for comp in self.comps:
        self.owidth = max(self.owidth, self.width + comp['x'])
        self.oheight = max(self.oheight, self.height + comp['y'])

    self.post_validate()

  def vpp(self):
    self.validate_caps()

    iopts         = self.gen_input_opts()
    oopts         = self.gen_output_opts()
    name          = self.gen_name().format(**vars(self))

    self.decoded = get_media()._test_artifact("{}.yuv".format(name))
    self.encoded = get_media()._test_artifact("{}.h264".format(name))
    self.call_ffmpeg(iopts.format(**vars(self)), oopts.format(**vars(self)))

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = md5(self.decoded)
      get_media()._set_test_details(md5_ref = md5ref)

      for i in range(1, self.r2r):
        self.decoded = get_media()._test_artifact("{}_{}.yuv".format(name, i))
        self.call_ffmpeg(iopts.format(**vars(self)), oopts.format(**vars(self)))
        result = md5(self.decoded)
        get_media()._set_test_details(**{ "md5_{:03}".format(i) : result})
        assert result == md5ref, "r2r md5 mismatch"
        #delete output file after each iteration
        get_media()._purge_test_artifact(self.decoded)
    else:
      self.check_metrics()
