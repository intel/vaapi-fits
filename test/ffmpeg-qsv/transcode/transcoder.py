###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
import os

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(using_compatible_driver)
@platform_tags(ALL_PLATFORMS)
class TranscoderTest(slash.Test):
  requirements = dict(
    decode = {
      "avc" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_decoder("h264"), "h264"),
        hw = (AVC_DECODE_PLATFORMS, have_ffmpeg_decoder("h264_qsv"), "h264_qsv"),
      ),
      "hevc-8" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_decoder("hevc"), "hevc"),
        hw = (HEVC_DECODE_8BIT_PLATFORMS, have_ffmpeg_decoder("hevc_qsv"), "hevc_qsv"),
      ),
      "mpeg2" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_decoder("mpeg2video"), "mpeg2video"),
        hw = (MPEG2_DECODE_PLATFORMS, have_ffmpeg_decoder("mpeg2_qsv"), "mpeg2_qsv"),
      ),
      "mjpeg" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_decoder("mjpeg"), "mjpeg"),
        hw = (JPEG_DECODE_PLATFORMS, have_ffmpeg_decoder("mjpeg_qsv"), "mjpeg_qsv"),
      ),
      "vc1" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_decoder("vc1"), "vc1"),
        hw = (VC1_DECODE_PLATFORMS, have_ffmpeg_decoder("vc1_qsv"), "vc1_qsv"),
      ),
    },
    encode = {
      "avc" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_encoder("libx264"), "libx264"),
        hw = (AVC_ENCODE_PLATFORMS, have_ffmpeg_encoder("h264_qsv"), "h264_qsv"),
      ),
      "hevc-8" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_encoder("libx265"), "libx265"),
        hw = (HEVC_ENCODE_8BIT_PLATFORMS, have_ffmpeg_encoder("hevc_qsv"), "hevc_qsv"),
      ),
      "mpeg2" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_encoder("mpeg2video"), "mpeg2video"),
        hw = (MPEG2_ENCODE_PLATFORMS, have_ffmpeg_encoder("mpeg2_qsv"), "mpeg2_qsv"),
      ),
      "mjpeg" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_encoder("mjpeg"), "mjpeg -global_quality 60"),
        hw = (JPEG_ENCODE_PLATFORMS, have_ffmpeg_encoder("mjpeg_qsv"), "mjpeg_qsv -global_quality 60"),
      ),
    },
    vpp = {
      "scale" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_filter("scale"), "scale=w={width}:h={height}"),
        hw = (VPP_PLATFORMS, have_ffmpeg_filter("vpp_qsv"), "vpp_qsv=w={width}:h={height}"),
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
        mode, ([], (False, "{}:{}:{}".format(ttype, codec, mode)), None))

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
      "avc"     : "h264",
      "hevc"    : "h265",
      "hevc-8"  : "h265",
      "mpeg2"   : "m2v",
      "mjpeg"   : "mjpeg",
    }.get(codec, "???")

  def validate_spec(self):
    from slash.utils.pattern_matching import Matcher

    assert len(self.outputs), "Invalid test case specification, outputs data empty"
    assert self.mode in ["sw", "hw"], "Invalid test case specification as mode type not valid"

    # generate platform list based on test runtime parameters
    iplats, ireq, _ =  self.get_requirements_data("decode", self.codec, self.mode)
    platforms = set(iplats)
    requires = [ireq,]

    for output in self.outputs:
      codec = output["codec"]
      mode  = output["mode"]
      assert mode in ["sw", "hw"], "Invalid test case specification as output mode type not valid"
      oplats, oreq, _ = self.get_requirements_data("encode", codec, mode)
      platforms &= set(oplats)
      requires.append(oreq)

      if output.get("width", None) is not None or output.get("height", None) is not None:
        oplats, oreq, _ = self.get_requirements_data("vpp", "scale", mode)
        platforms &= set(oplats)
        requires.append(oreq)

    # create matchers based on command-line filters
    matchers = [Matcher(s) for s in slash.config.root.run.filter_strings]

    # check if user supplied any platform tag on command line
    pmatch = any(map(lambda p: any([m.matches(p) for m in matchers]), ALL_PLATFORMS))

    # if user supplied a platform tag, check if this test can support it via the
    # test param-based required platforms
    if pmatch and not any(map(lambda p: any([m.matches(p) for m in matchers]), platforms)):
      slash.skip_test("unsupported platform")

    # check required
    if not all([t for t,m in requires]):
      slash.skip_test(
        "One or more software requirements not met: {}".format(
          str([m for t,m in requires if not t])))

  def gen_input_opts(self):
    opts = "-init_hw_device qsv=hw:/dev/dri/renderD128 -filter_hw_device hw"
    opts += " -hwaccel_output_format qsv"
    if "hw" == self.mode:
      opts += " -hwaccel qsv"
    opts += " -c:v {}".format(self.get_decoder(self.codec, self.mode))
    opts += " -i {source}"

    return opts.format(**vars(self))

  def gen_output_opts(self):
    self.goutputs = dict()

    opts = "-an"

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
        filters.extend(["format=nv12", "hwupload=extra_hw_frames=64"])

      vppscale = self.get_vpp_scale(
        output.get("width", None), output.get("height", None), mode)
      if vppscale is not None:
        filters.append(vppscale)

      for channel in xrange(output.get("channels", 1)):
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

  def transcode(self):
    self.validate_spec()
    iopts = self.gen_input_opts()
    oopts = self.gen_output_opts()

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)
    self.output = call("ffmpeg -v verbose {} {}".format(iopts, oopts))

    self.check_output()

    for n, output in enumerate(self.outputs):
      for channel in xrange(output.get("channels", 1)):
        encoded = self.goutputs[n][channel]
        yuv = get_media()._test_artifact(
          "{}_{}_{}.yuv".format(self.case, n, channel))
        vppscale = self.get_vpp_scale(self.width, self.height, "sw")
        call(
          "ffmpeg -v verbose -i {} -vf '{}' -pix_fmt yuv420p -f rawvideo"
          " -vframes {} -y {}".format(
            encoded, vppscale, self.frames, yuv))
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
