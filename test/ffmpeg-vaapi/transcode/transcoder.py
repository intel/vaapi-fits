###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
import os

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@platform_tags(ALL_PLATFORMS)
class TranscoderTest(slash.Test):
  requirements = dict(
    decode = {
      "avc" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_decoder("h264"), ("h264", None)),
        # for ffmpeg-vaapi HW decoders are built-in and can't be validated
        hw = (AVC_DECODE_PLATFORMS, (True, True), None),
      ),
      "hevc-8" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_decoder("hevc"), ("hevc", None)),
        # for ffmpeg-vaapi HW decoders are built-in and can't be validated
        hw = (HEVC_DECODE_8BIT_PLATFORMS, (True, True), None),
      ),
      "mpeg2" : dict(
        hw = (MPEG2_DECODE_PLATFORMS, (True, True), None),
      ),
      "vc1" : dict(
        hw = (VC1_DECODE_PLATFORMS, (True, True), None),
      ),
    },
    encode = {
      "avc" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_encoder("libx264"), ("libx264", "h264")),
        hw = (AVC_ENCODE_PLATFORMS, have_ffmpeg_encoder("h264_vaapi"), ("h264_vaapi", "h264")),
      ),
      "hevc-8" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_encoder("libx265"), ("libx265", "h265")),
        hw = (HEVC_ENCODE_8BIT_PLATFORMS, have_ffmpeg_encoder("hevc_vaapi"), ("hevc_vaapi", "h265")),
      ),
      "mpeg2" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_encoder("mpeg2video"), ("mpeg2video", "m2v")),
        hw = (MPEG2_ENCODE_PLATFORMS, have_ffmpeg_encoder("mpeg2_vaapi"), ("mpeg2_vaapi", "m2v")),
      ),
      "mjpeg" : dict(
        sw = (ALL_PLATFORMS, have_ffmpeg_encoder("mjpeg"), ("mjpeg", "mjpeg")),
        hw = (JPEG_ENCODE_PLATFORMS, have_ffmpeg_encoder("mjpeg_vaapi"), ("mjpeg_vaapi", "mjpeg")),
      ),
    }
  )

  # hevc implies hevc 8 bit
  requirements["encode"]["hevc"] = requirements["encode"]["hevc-8"]
  requirements["decode"]["hevc"] = requirements["decode"]["hevc-8"]

  def before(self):
    self.refctx = []
 
  def get_requirements_data(self, ttype, codec, mode):
    return  self.requirements[ttype].get(
      codec, {}).get(mode, ([], (False, False), None))

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
      slash.skip_test("One or more software requirements not met")

  def gen_input_opts(self):
    opts = ""

    if "hw" == self.mode:
      opts += " -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi"
    else:
      _, _, ffparms = self.get_requirements_data("decode", self.codec, self.mode)
      assert ffparms is not None, "decode parameters are empty"
      ffcodec, _ = ffparms
      opts += " -vaapi_device /dev/dri/renderD128 -c:v {}".format(ffcodec)

    opts += " -i {source}"

    return opts.format(**vars(self))

  def gen_output_opts(self):
    self.goutputs = dict()

    opts = "-an"

    for n, output in enumerate(self.outputs):
      codec = output["codec"]
      mode = output["mode"]

      _, _, ffparms = self.get_requirements_data("encode", codec, mode)
      assert ffparms is not None, "failed to find a suitable encoder"

      ffcodec, ext = ffparms

      for channel in xrange(output.get("channels", 1)):
        if "sw" == mode and "hw" == self.mode:
          opts += " -vf 'hwdownload,format=nv12'"
        elif "hw" == mode and "sw" == self.mode:
          opts += " -vf 'format=nv12,hwupload'"

        opts += " -c:v {}".format(ffcodec)
        opts += " -vframes {frames}"

        ofile = get_media()._test_artifact(
          "{}_{}_{}.{}".format(self.case, n, channel, ext))
        opts += " -y {}".format(ofile)

        self.goutputs.setdefault(n, list()).append(ofile)

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

    # source file to yuv
    self.srcyuv = get_media()._test_artifact(
      "src_{case}.yuv".format(**vars(self)))
    call(
      "ffmpeg -i {source} -pix_fmt yuv420p"
      " -vframes {frames} -y {srcyuv}".format(**vars(self)))

    for n, output in enumerate(self.outputs):
      for channel in xrange(output.get("channels", 1)):
        encoded = self.goutputs[n][channel]
        yuv = get_media()._test_artifact(
          "{}_{}_{}.yuv".format(self.case, n, channel))
        call(
          "ffmpeg -i {} -pix_fmt yuv420p -vframes {}"
          " -y {}".format(encoded, self.frames, yuv))
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
