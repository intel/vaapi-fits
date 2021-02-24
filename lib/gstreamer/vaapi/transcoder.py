###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from .util import *
import os

@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("checksumsink2"))
class TranscoderTest(slash.Test):
  requirements = dict(
    decode = {
      "avc" : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("avdec_h264"), "h264parse ! avdec_h264"),
        hw = (platform.get_caps("decode", "avc"), have_gst_element("vaapih264dec"), "h264parse ! vaapih264dec"),
      ),
      "hevc-8" : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("avdec_h265"), "h265parse ! avdec_h265"),
        hw = (platform.get_caps("decode", "hevc_8"), have_gst_element("vaapih265dec"), "h265parse ! vaapih265dec"),
      ),
      "mpeg2" : dict(
        sw = (dict(maxres = (2048, 2048)), have_gst_element("avdec_mpeg2video"), "mpegvideoparse ! avdec_mpeg2video"),
        hw = (platform.get_caps("decode", "mpeg2"), have_gst_element("vaapimpeg2dec"), "mpegvideoparse ! vaapimpeg2dec"),
      ),
      "mjpeg" : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("jpegdec"), "jpegparse ! jpegdec"),
        hw = (platform.get_caps("decode", "jpeg"), have_gst_element("vaapijpegdec"), "jpegparse ! vaapijpegdec"),
      ),
      "vc1" : dict(
        sw = (
          dict(maxres = (16384, 16384)), have_gst_element("avdec_vc1"),
          "'video/x-wmv,profile=(string)advanced'"
          ",width={width},height={height},framerate=14/1 ! avdec_vc1"
        ),
        hw = (
          platform.get_caps("decode", "vc1"), have_gst_element("vaapivc1dec"),
          "'video/x-wmv,profile=(string)advanced'"
          ",width={width},height={height},framerate=14/1 ! vaapivc1dec"
        ),
      ),
    },
    encode = {
      "avc" : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("x264enc"), "x264enc ! video/x-h264,profile=main ! h264parse"),
        hw = (platform.get_caps("encode", "avc"), have_gst_element("vaapih264enc"), "vaapih264enc ! video/x-h264,profile=main ! h264parse"),
      ),
      "hevc-8" : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("x265enc"), "videoconvert chroma-mode=none dither=0 ! video/x-raw,format=I420 ! x265enc ! video/x-h265,profile=main ! h265parse"),
        hw = (platform.get_caps("encode", "hevc_8"), have_gst_element("vaapih265enc"), "vaapih265enc ! video/x-h265,profile=main ! h265parse"),
      ),
      "mpeg2" : dict(
        sw = (dict(maxres = (2048, 2048)), have_gst_element("avenc_mpeg2video"), "avenc_mpeg2video ! mpegvideoparse"),
        hw = (platform.get_caps("encode", "mpeg2"), have_gst_element("vaapimpeg2enc"), "vaapimpeg2enc ! mpegvideoparse"),
      ),
      "mjpeg" : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("jpegenc"), "jpegenc ! jpegparse"),
        hw = (platform.get_caps("vdenc", "jpeg"), have_gst_element("vaapijpegenc"), "vaapijpegenc ! jpegparse"),
      ),
    },
    vpp = {
      "scale" : dict(
        sw = (True, have_gst_element("videoscale"), "videoscale ! video/x-raw,width={width},height={height}"),
        hw = (platform.get_caps("vpp", "scale"), have_gst_element("vaapipostproc"), "vaapipostproc ! video/x-raw,width={width},height={height}"),
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
      "mpeg2"          : "m2v",
      "mjpeg"          : "mjpeg",
    }.get(codec, "???")

  def validate_caps(self):
    assert len(self.outputs), "Invalid test case specification, outputs data empty"
    assert self.mode in ["sw", "hw"], "Invalid test case specification as mode type not valid"

    icaps, ireq, _ = self.get_requirements_data("decode", self.codec, self.mode)
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
        "Missing one or more required gstreamer elements: {}".format(list(unmet)))

  def gen_input_opts(self):
    opts = "filesrc location={source}"
    opts += " ! " + self.get_decoder(self.codec, self.mode)
    return opts.format(**vars(self))

  def gen_output_opts(self):
    self.goutputs = dict()
    opts = "tee name=transcoder"

    for n, output in enumerate(self.outputs):
      codec = output["codec"]
      mode  = output["mode"]
      encoder = self.get_encoder(codec, mode)
      ext = self.get_file_ext(codec)

      vppscale = self.get_vpp_scale(
        output.get("width", None), output.get("height", None), mode)

      for channel in range(output.get("channels", 1)):
        ofile = get_media()._test_artifact(
          "{}_{}_{}.{}".format(self.case, n, channel, ext))
        self.goutputs.setdefault(n, list()).append(ofile)

        opts += " ! queue max-size-buffers=0 max-size-bytes=0 max-size-time=0"
        if vppscale is not None:
          opts += " ! {}".format(vppscale)
        opts += " ! {}".format(encoder)
        opts += " ! filesink location={} transcoder.".format(ofile)

    # dump decoded source to yuv for reference comparison
    self.srcyuv = get_media()._test_artifact(
      "src_{case}.yuv".format(**vars(self)))
    opts += " ! queue max-size-buffers=0 max-size-bytes=0 max-size-time=0"
    opts += " ! videoconvert chroma-mode=none dither=0 ! video/x-raw,format=I420"
    opts += " ! checksumsink2 file-checksum=false qos=false eos-after={frames}"
    opts += " frame-checksum=false plane-checksum=false dump-output=true"
    opts += " dump-location={srcyuv}"

    return opts.format(**vars(self))

  @timefn("gst")
  def call_gst(self, iopts, oopts):
    call("gst-launch-1.0 -vf {iopts} ! {oopts}".format(
      iopts = iopts, oopts = oopts))

  def transcode(self):
    self.validate_caps()
    iopts = self.gen_input_opts()
    oopts = self.gen_output_opts()

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    self.call_gst(iopts, oopts)

    for n, output in enumerate(self.outputs):
      get_media()._set_test_details(**{"output.{}".format(n) : output})
      for channel in range(output.get("channels", 1)):
        encoded = self.goutputs[n][channel]
        yuv = get_media()._test_artifact(
          "{}_{}_{}.yuv".format(self.case, n, channel))
        iopts = "filesrc location={} ! {}"
        oopts =  "{} ! videoconvert chroma-mode=none dither=0 ! video/x-raw,format=I420"
        oopts += " ! checksumsink2 file-checksum=false qos=false eos-after={frames}"
        oopts += " frame-checksum=false plane-checksum=false dump-output=true"
        oopts += " dump-location={}"

        self.call_gst(
          iopts.format(encoded, self.get_decoder(output["codec"], "hw")),
          oopts.format(self.get_vpp_scale(self.width, self.height, "hw"), yuv, frames = self.frames))

        self.check_metrics(yuv, refctx = [(n, channel)])
        get_media()._purge_test_artifact(yuv)

  def check_metrics(self, yuv, refctx):
    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.srcyuv, yuv,
        self.width, self.height,
        self.frames),
      context = self.refctx + refctx,
    )
