###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash
import os

from ...lib.codecs import Codec
from ...lib.common import timefn, get_media, call, exe2os, filepath2os
from ...lib.formats import PixelFormat
from ...lib.gstreamer.util import BaseFormatMapper, have_gst, have_gst_element, parse_psnr_stats
from ...lib.gstreamer.util import gst_discover, gst_discover_fps
from ...lib import metrics2

@slash.requires(have_gst)
@slash.requires(*have_gst_element("checksumsink2"))
class BaseTranscoderTest(slash.Test, BaseFormatMapper):
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
    return scale.format(width = width or self.width, height = height or self.height, format = self.mformat)

  def get_file_ext(self, codec):
    return {
      Codec.AVC   : "h264",
      Codec.HEVC  : "h265",
      Codec.AV1   : "webm",
      Codec.MPEG2 : "m2v",
      Codec.MJPEG : "mjpeg",
      Codec.VP9   : "webm",
    }.get(codec, "???")

  def validate_caps(self):
    assert len(self.outputs), "Invalid test case specification, outputs data empty"
    assert self.mode in ["sw", "hw", "va_hw", "d3d11_hw", "dma"], "Invalid test case specification as mode type not valid"

    if self.mode == "dma" and get_media()._get_driver_name() == "d3d11":
      slash.skip_test(
        "d3d11 does not support dma caps")

    # FIXME: subclasses always assume 8 bit profiles and caps.  Need to add support for other bitdepths.
    self.format = PixelFormat(self.format)
    if self.format.bitdepth != 8:
      slash.skip_test(f"{self.format} ({self.format.bitdepth} bits) unsupported")

    self.mformat = self.map_format(self.format)

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

  def get_demuxer(self, fname):
    ext = os.path.splitext(fname)[1]
    return {
      ".ivf"  : " ! ivfparse",
      ".webm" : " ! matroskademux",
      ".ts"   : " ! tsdemux"
    }.get(ext, "")

  def gen_input_opts(self):
    self.ossource = filepath2os(self.source)

    opts =  "filesrc location={ossource}"
    opts += self.get_demuxer(self.source)
    opts += " ! " + self.get_decoder(self.codec, self.mode)

    if self.mode in ["hw", "sw"]:
      opts += " ! 'video/x-raw(ANY),format={mformat}'"

    # if input framerate is unknown, then set it explicitly (VIZ-20689)
    self.gstfps = gst_discover_fps(self.ossource)
    if self.gstfps.startswith("0"):
      self.gstfps = "30/1"
    opts += f" ! videorate ! 'video/x-raw(ANY),framerate={self.gstfps}'"

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
        ofile = get_media().artifacts.reserve(ext)
        self.goutputs.setdefault(n, list()).append(ofile)
        osofile = filepath2os(ofile)

        opts += " ! queue max-size-buffers=0 max-size-bytes=0 max-size-time=0"
        if vppscale is not None:
          opts += " ! {}".format(vppscale)
        opts += " ! {}".format(encoder)
        opts += " ! filesink location={} transcoder.".format(osofile)

    opts += " ! queue max-size-buffers=0 max-size-bytes=0 max-size-time=0"
    opts += f" ! fakevideosink qos=false num-buffers={self.frames} sync=0"

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
        self.check_resolution(output, encoded)
        self.check_metrics(output, encoded, refctx = [(n, channel)])

  def check_resolution(self, output, encoded):
    osencoded = filepath2os(encoded)
    props = [l.strip() for l in gst_discover(osencoded).split('\n')]
    width = output.get("width", self.width)
    height = output.get("height", self.height)

    assert "Width: {}".format(width) in props
    assert "Height: {}".format(height) in props

  def check_metrics(self, output, encoded, refctx):
    ocodec    = output["codec"]
    odecoder  = self.get_decoder(ocodec, "hw")
    osencoded = filepath2os(encoded)

    vppscale = self.get_vpp_scale(self.width, self.height, "hw")
    statsfile = get_media().artifacts.reserve("psnr")
    osstatsfile = filepath2os(statsfile)

    iopts = (
      f"filesrc location={osencoded} {self.get_demuxer(encoded)} ! {odecoder} ! {vppscale}"
      f" ! videorate ! 'video/x-raw(ANY),framerate={self.gstfps}' ! cmp."
      f" {self.gen_input_opts()} ! {vppscale} ! cmp."
      f" avvideocompare method=psnr stats-file={osstatsfile} name=cmp"
    )
    oopts = f"fakevideosink qos=false num-buffers={self.frames} sync=0"

    self.call_gst(iopts, oopts)

    metric = metrics2.factory.create(metric = dict(type = "psnr"), refctx = self.refctx + refctx)
    metric.actual = parse_psnr_stats(statsfile, self.frames)
    metric.check()
