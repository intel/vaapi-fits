###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash

from ...lib.common import timefn, get_media, call, exe2os, filepath2os
from ...lib.metrics import calculate_psnr
from ...lib.gstreamer.util import have_gst, have_gst_element, gst_discover

@slash.requires(have_gst)
@slash.requires(*have_gst_element("checksumsink2"))
class BaseTranscoderTest(slash.Test):
  def before(self):
    self.refctx = []
    self.post_validate = lambda: None
    vars(self).setdefault("format", "NV12")

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
    return scale.format(width = width or self.width, height = height or self.height, format = self.format)

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

    unmet = set([m for t,m in requires if not t])
    if len(unmet) != 0:
      slash.skip_test(
        "Missing one or more required gstreamer elements: {}".format(list(unmet)))

    self.post_validate()

  def gen_input_opts(self):
    self.ossource = filepath2os(self.source)
    opts =  "filesrc location={ossource}"
    opts += " ! " + self.get_decoder(self.codec, self.mode)
    opts += " ! video/x-raw,format={format}"
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
        osofile = filepath2os(ofile)

        opts += " ! queue max-size-buffers=0 max-size-bytes=0 max-size-time=0"
        if vppscale is not None:
          opts += " ! {}".format(vppscale)
        opts += " ! {}".format(encoder)
        opts += " ! filesink location={} transcoder.".format(osofile)

    # dump decoded source to yuv for reference comparison
    self.srcyuv = get_media()._test_artifact(
      "src_{case}.yuv".format(**vars(self)))
    self.ossrcyuv = filepath2os(self.srcyuv)
    opts += " ! queue max-size-buffers=0 max-size-bytes=0 max-size-time=0"
    opts += " ! checksumsink2 file-checksum=false qos=false eos-after={frames}"
    opts += " frame-checksum=false plane-checksum=false dump-output=true"
    opts += " dump-location={ossrcyuv}"

    return opts.format(**vars(self))

  @timefn("gst")
  def call_gst(self, iopts, oopts):
    call(f"{exe2os('gst-launch-1.0')}"
         " -vf {iopts} ! {oopts}".format(
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
        osencoded = filepath2os(encoded)
        yuv = get_media()._test_artifact(
          "{}_{}_{}.yuv".format(self.case, n, channel))
        osyuv = filepath2os(yuv)
        iopts = "filesrc location={} ! {}"
        oopts = self.get_vpp_scale(self.width, self.height, "hw")
        oopts += " ! checksumsink2 file-checksum=false qos=false eos-after={frames}"
        oopts += " frame-checksum=false plane-checksum=false dump-output=true"
        oopts += " dump-location={}"
        self.call_gst(
          iopts.format(osencoded, self.get_decoder(output["codec"], "hw")),
          oopts.format(osyuv, frames = self.frames))
        self.check_resolution(output, osencoded)
        self.check_metrics(yuv, refctx = [(n, channel)])
        get_media()._purge_test_artifact(yuv)

  def check_resolution(self, output, encoded):
    props = [l.strip() for l in gst_discover(encoded).split('\n')]
    width = output.get("width", self.width)
    height = output.get("height", self.height)

    assert "Width: {}".format(width) in props
    assert "Height: {}".format(height) in props

  def check_metrics(self, yuv, refctx):
    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.srcyuv, yuv,
        self.width, self.height,
        self.frames, self.format),
      context = self.refctx + refctx,
    )
