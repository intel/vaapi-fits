###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
import os

@slash.requires(have_gst)
@slash.requires(*have_gst_element("msdk"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@platform_tags(ALL_PLATFORMS)
class TranscoderTest(slash.Test):
  requirements = dict(
    decode = {
      "avc" : dict(
        sw = (ALL_PLATFORMS, have_gst_element("avdec_h264"), ("h264parse ! avdec_h264", None)),
        hw = (AVC_DECODE_PLATFORMS, have_gst_element("msdkh264dec"), ("h264parse ! msdkh264dec", None)),
      ),
      "hevc-8" : dict(
        sw = (ALL_PLATFORMS, have_gst_element("avdec_h265"), ("h265parse ! avdec_h265", None)),
        hw = (HEVC_DECODE_8BIT_PLATFORMS, have_gst_element("msdkh265dec"), ("h265parse ! msdkh265dec", None)),
      ),
      "mpeg2" : dict(
        hw = (MPEG2_DECODE_PLATFORMS, have_gst_element("msdkmpeg2dec"), ("mpegvideoparse ! msdkmpeg2dec", None)),
      ),
      "mjpeg" : dict(
        hw = (JPEG_DECODE_PLATFORMS, have_gst_element("msdkmjpegdec"), ("jpegparse ! msdkmjpegdec", None)),
      ),
      "vc1" : dict(
        hw = (VC1_DECODE_PLATFORMS, have_gst_element("msdkvc1dec"), ("'video/x-wmv,profile=(string)advanced',width={width},height={height},framerate=14/1 ! msdkvc1dec", None)),
      ),
    },
    encode = {
      "avc" : dict(
        sw = (ALL_PLATFORMS, have_gst_element("x264enc"), ("x264enc ! video/x-h264,profile=main ! h264parse", "h264")),
        hw = (AVC_ENCODE_PLATFORMS, have_gst_element("msdkh264enc"), ("msdkh264enc ! video/x-h264,profile=main ! h264parse", "h264")),
      ),
      "hevc-8" : dict(
        sw = (ALL_PLATFORMS, have_gst_element("x265enc"), ("x265enc ! video/x-h265,profile=main ! h265parse", "h265")),
        hw = (HEVC_ENCODE_8BIT_PLATFORMS, have_gst_element("msdkh265enc"), ("msdkh265enc ! video/x-h265,profile=main ! h265parse", "h265")),
      ),
      "mpeg2" : dict(
        sw = (ALL_PLATFORMS, have_gst_element("avenc_mpeg2video"), ("avenc_mpeg2video ! mpegvideoparse", "m2v")),
        hw = (MPEG2_ENCODE_PLATFORMS, have_gst_element("msdkmpeg2enc"), ("msdkmpeg2enc ! mpegvideoparse", "m2v")),
      ),
      "mjpeg" : dict(
        sw = (ALL_PLATFORMS, have_gst_element("jpegenc"), ("jpegenc ! jpegparse", "mjpeg")),
        hw = (JPEG_ENCODE_PLATFORMS, have_gst_element("msdkmjpegenc"), ("msdkmjpegenc ! jpegparse", "mjpeg")),
      ),
    }
  )

  # hevc implies hevc 8 bit
  requirements["encode"]["hevc"] = requirements["encode"]["hevc-8"]
  requirements["decode"]["hevc"] = requirements["decode"]["hevc-8"]

  def before(self):
    self.refctx = []
  
  def get_requirements_data(self, ttype, codec, mode):
    return self.requirements[ttype].get(
      codec, {}).get(mode, ([], (False, False), None))

  def validate_spec(self):
    from slash.utils.pattern_matching import Matcher

    assert len(self.outputs), "Invalid test case specification, outputs data empty"
    if len(self.outputs) > 1 or self.outputs[0].get("channels", 1) > 1:
      slash.skip_test("transcode 1ton tests not supported")
    assert self.mode in ["sw", "hw"], "Invalid test case specification as mode type not valid"

    # generate platform list based on test runtime parameters
    iplats, ireq, _ =  self.get_requirements_data("decode", self.codec, self.mode)
    platforms = set(iplats)
    requires = [ireq,]

    codec = self.outputs[0]["codec"]
    mode  = self.outputs[0]["mode"]
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
    opts = " -vf filesrc location={source}"
    _, _, ffdecparms = self.get_requirements_data("decode", self.codec, self.mode)
    assert ffdecparms is not None, "decode parameters are empty"
    ffdecoder, _ = ffdecparms
    opts += " ! {}".format(ffdecoder)

    return opts.format(**vars(self))

  def gen_output_opts(self):
    opts = ""
    codec = self.outputs[0]["codec"]
    mode  = self.outputs[0]["mode"]
    _, _, ffencparms = self.get_requirements_data("encode", codec, mode)
    assert ffencparms is not None, "failed to find a suitable encoder"
    ffencoder, ext = ffencparms
    opts += " ! {}".format(ffencoder)
    self.ofile = get_media()._test_artifact(
      "{}.{}".format(self.case, ext))
    opts += " ! filesink location={ofile}"

    return opts.format(**vars(self))

  def gen_refyuv_decode_commands(self, codec, mode):
    refyuv_cmnd = ""
    _, _, ffdecparms = self.get_requirements_data("decode", codec, mode)
    ffdecoder, _ = ffdecparms
    refyuv_cmnd = " {}".format(ffdecoder)

    return refyuv_cmnd.format(**vars(self))
    
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
    self.output = call("gst-launch-1.0 -vf {} {}".format(iopts, oopts))

    # source file to yuv
    self.srcyuv = get_media()._test_artifact(
      "src_{case}.yuv".format(**vars(self)))
    # reference yuv generated using HW codec irrespective of mode passed from user-spec
    self.refyuv_decode_arg = self.gen_refyuv_decode_commands(self.codec, "hw")
    call(
      "gst-launch-1.0 -vf filesrc location={source}"
      " ! {refyuv_decode_arg}"
      " ! videoconvert ! video/x-raw,format=I420"
      " ! checksumsink2 file-checksum=false qos=false"
      " frame-checksum=false plane-checksum=false dump-output=true"
      " dump-location={srcyuv}".format(**vars(self)))

    yuv = get_media()._test_artifact(
      "{}.yuv".format(self.case))
    refyuv_decode_arg = self.gen_refyuv_decode_commands(self.outputs[0]["codec"], "hw")
    call(
      "gst-launch-1.0 -vf filesrc location={}"
      " ! {}"
      " ! videoconvert ! video/x-raw,format=I420"
      " ! checksumsink2 file-checksum=false qos=false"
      " frame-checksum=false plane-checksum=false dump-output=true"
      " dump-location={}".format(self.ofile, refyuv_decode_arg, yuv))
    self.check_metrics(yuv)

  def check_metrics(self, yuv):
    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.srcyuv, yuv,
        self.width, self.height,
        self.frames),
      context = self.refctx,
    )
