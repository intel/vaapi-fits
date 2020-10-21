###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from .util import *
import os

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
class TranscoderTest(slash.Test):
  requirements = dict(
    # ffmpeg-vaapi HW decoders are built-in
    decode = {
      "avc" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_decoder("h264"), "h264"),
        hw = (platform.get_caps("decode", "avc"), have_ffmpeg_decoder("h264"), "h264"),
      ),
      "hevc-8" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_decoder("hevc"), "hevc"),
        hw = (platform.get_caps("decode", "hevc_8"), have_ffmpeg_decoder("hevc"), "hevc"),
      ),
      "hevc-8-vme-ldb" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_decoder("hevc"), "hevc"),
        hw = (platform.get_caps("decode", "hevc_8"), have_ffmpeg_decoder("hevc"), "hevc"),
      ),
      "mpeg2" : dict(
        sw = (dict(maxres = (2048, 2048)), have_ffmpeg_decoder("mpeg2video"), "mpeg2video"),
        hw = (platform.get_caps("decode", "mpeg2"), have_ffmpeg_decoder("mpeg2video"), "mpeg2video"),
      ),
      "mjpeg" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_decoder("mjpeg"), "mjpeg"),
        hw = (platform.get_caps("decode", "jpeg"), have_ffmpeg_decoder("mjpeg"), "mjpeg"),
      ),
      "vc1" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_decoder("vc1"), "vc1"),
        hw = (platform.get_caps("decode", "vc1"), have_ffmpeg_decoder("vc1"), "vc1"),
      ),
    },
    encode = {
      "avc" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_encoder("libx264"), "libx264"),
        hw = (platform.get_caps("encode", "avc"), have_ffmpeg_encoder("h264_vaapi"), "h264_vaapi"),
      ),
      "hevc-8" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_encoder("libx265"), "libx265"),
        hw = (platform.get_caps("encode", "hevc_8"), have_ffmpeg_encoder("hevc_vaapi"), "hevc_vaapi"),
      ),
      "hevc-8-vme-ldb" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_encoder("libx265"), "libx265"),
        hw = (platform.get_caps("vme_lowdelayb", "hevc_8"), have_ffmpeg_encoder("hevc_vaapi"), "hevc_vaapi -b_strategy 1"),
      ),
      "mpeg2" : dict(
        sw = (dict(maxres = (2048, 2048)), have_ffmpeg_encoder("mpeg2video"), "mpeg2video"),
        hw = (platform.get_caps("encode", "mpeg2"), have_ffmpeg_encoder("mpeg2_vaapi"), "mpeg2_vaapi"),
      ),
      "mjpeg" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_encoder("mjpeg"), "mjpeg"),
        hw = (platform.get_caps("vdenc", "jpeg"), have_ffmpeg_encoder("mjpeg_vaapi"), "mjpeg_vaapi"),
      ),
    },
    vpp = {
      "scale" : dict(
        sw = (True, have_ffmpeg_filter("scale"), "scale=w={width}:h={height}"),
        hw = (platform.get_caps("vpp", "scale"), have_ffmpeg_filter("scale_vaapi"), "scale_vaapi=w={width}:h={height}"),
      ),
    },
  )

  # hevc implies hevc 8 bit
  requirements["encode"]["hevc"] = requirements["encode"]["hevc-8"]
  requirements["decode"]["hevc"] = requirements["decode"]["hevc-8"]

  def before(self):
    self.refctx = []
 
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

  def get_file_ext(self, codec):
    return {
      "avc"            : "h264",
      "hevc"           : "h265",
      "hevc-8"         : "h265",
      "hevc-8-vme-ldb" : "h265",
      "mpeg2"          : "m2v",
      "mjpeg"          : "mjpeg",
    }.get(codec, "???")

  def validate_caps(self):
    assert len(self.outputs), "Invalid test case specification, outputs data empty"
    assert self.mode in ["sw", "hw"], "Invalid test case specification as mode type not valid"

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
      assert mode in ["sw", "hw"], "Invalid test case specification as output mode type not valid"
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

    # check required
    unmet = set([m for t,m in requires if not t])
    if len(unmet) != 0:
      slash.skip_test(
        "Missing one or more required ffmpeg elements: {}".format(list(unmet)))

  def gen_input_opts(self):
    opts = "-init_hw_device vaapi=hw:/dev/dri/renderD128 -filter_hw_device hw"
    opts += " -hwaccel_output_format vaapi"
    if "hw" == self.mode:
      opts += " -hwaccel vaapi"
    opts += " -c:v {}".format(self.get_decoder(self.codec, self.mode))
    opts += " -i {source}"

    return opts.format(**vars(self))

  def gen_output_opts(self):
    self.goutputs = dict()

    opts = "-an -vsync passthrough"

    for n, output in enumerate(self.outputs):
      codec = output["codec"]
      mode = output["mode"]
      encoder = self.get_encoder(codec, mode)
      ext = self.get_file_ext(codec)

      filters = []
      tmode = (self.mode, mode)

      if ("hw", "sw") == tmode:   # HW to SW transcode
        filters.extend(["hwdownload", "format=nv12"])
      elif ("sw", "hw") == tmode: # SW to HW transcode
        filters.extend(["format=nv12", "hwupload"])

      vppscale = self.get_vpp_scale(
        output.get("width", None), output.get("height", None), mode)
      if vppscale is not None:
        filters.append(vppscale)

      for channel in range(output.get("channels", 1)):
        ofile = get_media()._test_artifact(
          "{}_{}_{}.{}".format(self.case, n, channel, ext))
        self.goutputs.setdefault(n, list()).append(ofile)

        if len(filters):
          opts += " -vf '{}'".format(','.join(filters))
        opts += " -c:v {}".format(encoder)
        opts += " -vframes {frames}"
        opts += " -y {}".format(ofile)

    # dump decoded source to yuv for reference comparison
    self.srcyuv = get_media()._test_artifact(
      "src_{case}.yuv".format(**vars(self)))
    if "hw" == self.mode:
      opts += " -vf 'hwdownload,format=nv12'"
    opts += " -pix_fmt yuv420p -f rawvideo"
    opts += " -vframes {frames} -y {srcyuv}"

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
    return call("ffmpeg -v verbose {} {}".format(iopts, oopts))

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
        yuv = get_media()._test_artifact(
          "{}_{}_{}.yuv".format(self.case, n, channel))
        vppscale = self.get_vpp_scale(self.width, self.height, "sw")
        iopts = "-i {}"
        oopts = "-vf '{}' -pix_fmt yuv420p -f rawvideo -vframes {} -y {}"
        self.call_ffmpeg(
          iopts.format(encoded), oopts.format(vppscale, self.frames, yuv))
        self.check_metrics(yuv, refctx = [(n, channel)])
        # delete yuv file after each iteration
        get_media()._purge_test_artifact(yuv)

  def check_metrics(self, yuv, refctx):
    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.srcyuv, yuv,
        self.width, self.height,
        self.frames),
      context = self.refctx + refctx,
    )
