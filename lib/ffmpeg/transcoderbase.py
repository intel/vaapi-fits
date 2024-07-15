###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re
import slash

from ...lib.common import timefn, get_media, call, exe2os, filepath2os
from ...lib.ffmpeg.util import BaseFormatMapper, have_ffmpeg, ffmpeg_probe_resolution, parse_psnr_stats

from ...lib import metrics2
from ...lib.parameters import format_value
from ...lib.codecs import Codec

@slash.requires(have_ffmpeg)
class BaseTranscoderTest(slash.Test,BaseFormatMapper):
  def before(self):
    super().before()
    self.refctx = []
    self.post_validate = lambda: None
    self.hwdevice = f"hw:{get_media().render_device}"
    self.format = "NV12"
    self.hdr = False

  def get_requirements_data(self, ttype, codec, mode):
    return  self.requirements[ttype].get(
      codec, {}).get(
        mode, (None, (False, "{}:{}:{}".format(ttype, codec, mode)), None))

  def get_decoder(self, codec, mode):
    _, _, decoder = self.get_requirements_data("decode", codec, mode)
    assert decoder is not None, "failed to find a suitable decoder: {}:{}".format(codec, mode)
    return decoder.format(**vars(self))

  def get_encoder(self, codec, mode):
    _, _, encoder = self.get_requirements_data("encode", codec, mode)
    assert encoder is not None, "failed to find a suitable encoder: {}:{}".format(codec, mode)
    return encoder.format(**vars(self))

  def get_vpp_scale(self, width, height, mode):
    if width is None and height is None:
      return None
    _, _, scale = self.get_requirements_data("vpp", "scale", mode)
    assert scale is not None, "failed to find a suitable vpp scaler: {}".format(mode)
    return scale.format(width = width or self.width, height = height or self.height)

  def get_tonemap(self, tm, fmt, mode):
    _, _, tonemap = self.get_requirements_data("tonemap", tm, mode)
    assert tonemap is not None, f"failed to find a suitable tonemapping method: {tm}:{mode}"
    return tonemap.format(format = fmt)

  def get_file_ext(self, codec):
    return {
      Codec.AVC   : "h264",
      Codec.HEVC  : "h265",
      Codec.MPEG2 : "m2v",
      Codec.MJPEG : "mjpeg",
      Codec.VP9   : "ivf",
      Codec.AV1   : "ivf"
    }.get(codec, "???")

  def validate_caps(self):
    assert len(self.outputs), "Invalid test case specification, outputs data empty"
    assert self.mode in ["sw", "hw", "lp", "va_hw", "d3d11_hw"], "Invalid test case specification as mode type not valid"

    icaps, ireq, _ =  self.get_requirements_data("decode", self.codec, self.mode)
    requires = [ireq,]

    if icaps is None:
      slash.skip_test(
        "decode.{codec}.{mode} unsupported".format(**vars(self)))

    maxw, maxh = icaps["maxres"]
    if self.width > maxw or self.height > maxh:
      slash.skip_test(
        "decode.{codec}.{mode}.{width}x{height} unsupported".format(**vars(self)))

    for output in self.outputs:
      codec = output["codec"]
      mode  = output["mode"]
      assert mode in ["sw", "hw", "lp"], "Invalid test case specification as output mode type not valid"
      ocaps, oreq, _ = self.get_requirements_data("encode", codec, mode)
      requires.append(oreq)

      if ocaps is None:
        slash.skip_test(
          "encode.{codec}.{mode} unsupported".format(codec = codec, mode = mode))

      maxw, maxh = ocaps["maxres"]
      w = output.get("width", None)
      h = output.get("height", None)
      if (w or self.width) > maxw or (h or self.height) > maxh:
        slash.skip_test(
          "encode.{codec}.{mode}.{width}x{height} unsupported".format(
            codec = codec, mode = mode,
            width = (w or self.width),
            height = (h or self.height)))

      if w is not None or h is not None:
        ocaps, oreq, _ = self.get_requirements_data("vpp", "scale", mode)
        requires.append(oreq)

        if ocaps is None:
          slash.skip_test(
            "vpp.scale.{mode} unsupported".format(mode = mode))

      tm = output.get("tonemap", None)
      if tm is not None:
        ocaps, oreq, _ = self.get_requirements_data("tonemap", tm, mode)
        requires.append(oreq)

        if ocaps is None:
          slash.skip_test(f"vpp.tonemap.{mode}.{tm} unsupported")

    # check required
    unmet = set([m for t,m in requires if not t])
    if len(unmet) != 0:
      slash.skip_test(
        "Missing one or more required ffmpeg elements: {}".format(list(unmet)))

    self.post_validate()

  def gen_input_opts(self):
    if self.mode in ["va_hw", "d3d11_hw"]:
      if "va_hw" == self.mode:
        hw = "vaapi"
        hwformat = "vaapi"
      else:
        hw = "d3d11va"
        hwformat = "d3d11"
      opts = f"-init_hw_device {hw}={hw},child_device={get_media().render_device}"
      opts += f" -init_hw_device {self.hwaccel}={self.hwaccel}@{hw}"
      opts += f" -hwaccel_output_format {hwformat}"
      opts += f" -hwaccel {hw}"
    else:
      opts = "-init_hw_device {hwaccel}={hwdevice}"
      opts += " -hwaccel_output_format {hwaccel}"
    if "hw" == self.mode:
      opts += " -hwaccel {hwaccel}"
      if vars(self).get("ihwframes", None) is not None:
        opts += " -extra_hw_frames {ihwframes}"
    opts += " -c:v {}".format(self.get_decoder(self.codec, self.mode))
    opts += f" -i {filepath2os(self.source)}"

    return opts.format(**vars(self))

  def gen_output_opts(self):
    self.goutputs = dict()
    iformat = self.map_format(self.format)
    opts = "-an"

    for n, output in enumerate(self.outputs):
      codec = output["codec"]
      mode = output["mode"]
      encoder = self.get_encoder(codec, mode)
      ext = self.get_file_ext(codec)
      filters = []
      tmode = (self.mode, mode)

      # WA: LDB is not enabled by default for HEVCe on gen11+, yet.
      if Codec.HEVC == codec and get_media()._get_gpu_gen() > 10:
        encoder += " -b_strategy 1"
      if "lp" == mode:
        encoder += " -low_power 1"

      tmap = output.get("tonemap", None)
      if tmap is not None:
        oformat = self.map_format(output.get("format", self.format))
        tonemap = self.get_tonemap(tmap, oformat, mode)
        filters.append(tonemap)
      elif ("hw", "sw") == tmode:   # HW to SW transcode
        filters.extend(["hwdownload", f"format={iformat}"])
      elif ("sw", "hw") == tmode: # SW to HW transcode
        filters.extend([f"format={iformat}", "hwupload"])
        if vars(self).get("ohwframes", None) is not None:
          filters[-1] += "=extra_hw_frames={ohwframes}"

      vppscale = self.get_vpp_scale(
        output.get("width", None), output.get("height", None), mode)
      if vppscale is not None:
        filters.append(vppscale)

      for channel in range(output.get("channels", 1)):
        ofile = get_media().artifacts.reserve(ext)
        self.goutputs.setdefault(n, list()).append(ofile)
        osofile = filepath2os(ofile)

        if len(filters):
          opts += " -vf '{}'".format(','.join(filters))

        opts += " -fps_mode passthrough"
        opts += " -c:v {}".format(encoder)
        opts += " -vframes {frames}"
        opts += " -y {}".format(osofile)

    return opts.format(**vars(self))

  def check_output(self):
    m = re.search(
      "not supported for hardware decode", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"

    m = re.search(
      "hwaccel initialisation returned error", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"

  @timefn("ffmpeg")
  def call_ffmpeg(self, iopts, oopts):
    return call(f"{exe2os('ffmpeg')}"
                " -v verbose {} {}".format(iopts, oopts))

  def transcode(self):
    self.validate_caps()
    iopts = self.gen_input_opts()
    oopts = self.gen_output_opts()

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)
    self.output = self.call_ffmpeg(iopts, oopts)

    self.check_output()

    for n, output in enumerate(self.outputs):
      get_media()._set_test_details(**{"output.{}".format(n) : output})

      for channel in range(output.get("channels", 1)):
        encoded = self.goutputs[n][channel]
        osencoded = filepath2os(encoded)

        self.check_resolution(output, osencoded)
        self.check_hdr(output, osencoded)
        self.check_metrics(output, osencoded, refctx = [(n, channel)])

  def check_resolution(self, output, encoded):
    actual = ffmpeg_probe_resolution(encoded)
    expect = "{}x{}".format(
      output.get("width", self.width), output.get("height", self.height))
    assert expect == actual

  def check_hdr(self, output, encoded):
    if output.get("tonemap", None) is not None:
      get_media()._set_test_details(**{"hdr.info:expect" : "no"})
      # make sure the output is a SDR file
      output_mdm_info, output_cll_info = self.get_hdr_info(encoded)
      assert len(output_mdm_info) == 0 and len(output_cll_info) == 0, "Found HDR information in output video, h2s failed"
    elif vars(self).get("hdr", False):
      get_media()._set_test_details(**{"hdr.info:expect" : "yes"})
      input_mdm_info, input_cll_info = self.get_hdr_info(filepath2os(self.source))
      assert len(input_mdm_info) + len(input_cll_info) > 0, "Found no HDR information in input video"

      output_mdm_info, output_cll_info = self.get_hdr_info(encoded)
      assert len(output_mdm_info) + len(output_cll_info) > 0, "Found no HDR information in output video"

      assert (len(input_mdm_info) == 0 or (len(input_mdm_info) == len(output_mdm_info) and input_mdm_info[0] == output_mdm_info[0])) and \
        (len(input_cll_info) == 0 or (len(input_cll_info) == len(output_cll_info) and input_cll_info[0] == output_cll_info[0])), "HDR info is different between input and output"

  def check_metrics(self, output, encoded, refctx):
    tfilters  = []
    rfilters  = []
    iopts     = ""
    oformat   = self.map_format(output.get("format", self.format))
    ocodec    = output["codec"]

    # WA: FFMpeg does not have an AV1 SW decoder
    if ocodec in [Codec.AV1]:
      # NOTE: init_hw_device will already be added by gen_input_opts, called later (assuming no user reference is defined).
      iopts = f"-hwaccel {self.hwaccel} -hwaccel_output_format {self.hwaccel} -c:v {self.get_decoder(ocodec, 'hw')}"
      tfilters.extend(["hwdownload", f"format={oformat}"])

    # Decode the encoded result and use fps=1 so the psnr filter does not try to guess different rates for each input.
    iopts += f" -r:v 1 -i {encoded} "

    if vars(self).get("reference", None) is not None:
      ref = format_value(self.reference, case = self.case, **output)
      osref = filepath2os(ref)
      # Decode the user-supplied reference and use fps=1 so the psnr filter does not try to guess different rates for each input.
      iopts += f" -r:v 1 -f rawvideo -pix_fmt {oformat} -s:v {self.width}x{self.height} -i {osref}"
      rfilters.append(f"format={oformat}")
      tfilters.append(f"format={oformat}")
    else:
      # Decode the original source and use fps=1 so the psnr filter does not try to guess different rates for each input.
      iopts += f" -r:v 1 {self.gen_input_opts()}"
      if self.mode in ["va_hw", "d3d11_hw", "hw"]:
        rfilters.extend(["hwdownload", f"format={oformat}"])

    # scale the encoded result back to the original source resolution
    vppscale = self.get_vpp_scale(self.width, self.height, "sw")
    if ocodec in [Codec.JPEG, Codec.MJPEG]:
      vppscale += ":in_range=pc:out_range=pc"
    tfilters.append(vppscale)
    rfilters.append(vppscale)

    statsfile = get_media().artifacts.reserve("psnr")

    # generate the inline psnr filter
    oopts = f" -lavfi '[0:v]{','.join(tfilters)}[test];[1:v]{','.join(rfilters)}[ref];[test][ref]psnr=f={statsfile}:shortest=1'"
    oopts += f" -fps_mode passthrough -noautoscale -vframes {self.frames} -f null -"

    self.call_ffmpeg(iopts, oopts)

    metric = metrics2.factory.create(metric = dict(type = "psnr"), refctx = self.refctx + refctx)
    metric.actual = parse_psnr_stats(statsfile, self.frames)
    metric.check()

  def get_hdr_info(self, osfile):
    output = call(
      f"{exe2os('ffmpeg')} -an -i {osfile}"
      f" -vf 'showinfo' -vframes 1 -f null -"
    )

    mdm_info = re.findall(r'(?<=side data - Mastering display metadata: ).*', output)
    cll_info = re.findall(r'(?<=side data - Content light level metadata: ).*', output)

    return mdm_info, cll_info
