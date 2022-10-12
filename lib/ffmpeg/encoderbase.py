###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import re
import slash

from ...lib.common import get_media, timefn, call, exe2os, filepath2os
from ...lib.ffmpeg.util import have_ffmpeg, BaseFormatMapper
from ...lib.ffmpeg.util import parse_inline_md5, parse_psnr_stats
from ...lib.ffmpeg.decoderbase import Decoder
from ...lib.parameters import format_value
from ...lib.properties import PropertyHandler
from ...lib.util import skip_test_if_missing_features

from ...lib import metrics2

class Encoder(PropertyHandler, BaseFormatMapper):
  # required properties
  ffencoder     = property(lambda s: s.props["ffencoder"])
  codec         = property(lambda s: s.props["codec"])
  frames        = property(lambda s: s.props["frames"])
  format        = property(lambda s: s.map_format(s.props["format"]))
  hwaccel       = property(lambda s: s.props["hwaccel"])
  hwdevice      = property(lambda s: get_media().render_device)
  source        = property(lambda s: s.props["source"])
  ossource      = property(lambda s: filepath2os(s.source))
  width         = property(lambda s: s.props["width"])
  height        = property(lambda s: s.props["height"])
  rcmode        = property(lambda s: s.props['rcmode'].upper())
  encoded       = property(lambda s: s._encoded)
  osencoded     = property(lambda s: filepath2os(s.encoded))
  encoded_ext   = property(lambda s: s.props["encoded_ext"])

  @property
  def hwformat(self):
    # BUG: It appears there's a ffmpeg bug with yuv420p hwupload when using
    # i965 driver.  Need to report upstream ffmpeg!
    ifmts = self.props["caps"]["fmts"]
    if "i965" == get_media()._get_driver_name():
      ifmts = list(set(ifmts) - set(["I420"]))
    return self.map_best_hw_format(self.props["format"], ifmts)

  # optional properties
  fps           = property(lambda s: s.ifprop("fps", " -r:v {fps}"))
  profile       = property(lambda s: s.ifprop("profile", " -profile:v {profile}"))
  gop           = property(lambda s: s.ifprop("gop", " -g {gop}"))
  extbrc        = property(lambda s: s.ifprop("extbrc", " -extbrc {extbrc}"))
  slices        = property(lambda s: s.ifprop("slices", " -slices {slices}"))
  bframes       = property(lambda s: s.ifprop("bframes", " -bf {bframes}"))
  minrate       = property(lambda s: s.ifprop("minrate", " -b:v {minrate}k"))
  maxrate       = property(lambda s: s.ifprop("maxrate", " -maxrate {maxrate}k"))
  refs          = property(lambda s: s.ifprop("refs", " -refs {refs}"))
  lowpower      = property(lambda s: s.ifprop("lowpower", " -low_power {lowpower}"))
  loopshp       = property(lambda s: s.ifprop("loopshp", " -loop_filter_sharpness {loopshp}"))
  looplvl       = property(lambda s: s.ifprop("looplvl", " -loop_filter_level {looplvl}"))
  level         = property(lambda s: s.ifprop("level", " -level {level}"))
  ladepth       = property(lambda s: s.ifprop("ladepth", " -look_ahead 1 -look_ahead_depth {ladepth}"))
  forced_idr    = property(lambda s: s.ifprop("vforced_idr", " -forced_idr 1 -force_key_frames expr:1"))
  maxframesize  = property(lambda s: s.ifprop("maxframesize", " -max_frame_size {maxframesize}k"))
  pict          = property(lambda s: s.ifprop("vpict", " -pic_timing_sei 0"))
  roi           = property(lambda s: s.ifprop("roi", ",addroi=0:0:{width}/2:{height}/2:-1/3"))
  strict        = property(lambda s: s.ifprop("strict", " -strict {strict}"))
  hwupload      = property(lambda s: ",hwupload")

  @property
  def rqp(self):
    def inner(rqp):
      return (
        f" -max_qp_i {rqp['MaxQPI']}"
        f" -min_qp_i {rqp['MinQPI']}"
        f" -max_qp_p {rqp['MaxQPP']}"
        f" -min_qp_p {rqp['MinQPP']}"
        f" -max_qp_b {rqp['MaxQPB']}"
        f" -min_qp_b {rqp['MinQPB']}"
      )
    return self.ifprop("rqp", inner)

  @property
  def intref(self):
    def inner(intref):
      return (
        f" -int_ref_type {intref['type']}"
        f" -int_ref_cycle_size {intref['size']}"
        f" -int_ref_cycle_dist {intref['dist']}"
      )
    return self.ifprop("intref", inner)

  @property
  def hwinit(self):
    return (
      f"-hwaccel {self.hwaccel}"
      f" -init_hw_device {self.hwaccel}=hw:{self.hwdevice}"
      f" -hwaccel_output_format {self.hwaccel}"
    )

  @property
  def encparams(self):
    return (
      f"{self.profile}{self.qp}{self.quality}{self.gop}"
      f"{self.bframes}{self.slices}{self.minrate}{self.maxrate}{self.refs}"
      f"{self.extbrc}{self.loopshp}{self.looplvl}{self.tilecols}{self.tilerows}"
      f"{self.level}{self.ladepth}{self.forced_idr}{self.intref}{self.lowpower}"
      f"{self.maxframesize}{self.pict}{self.rqp}{self.strict}"
    )

  @property
  def ffoutput(self):
    if self.props.get("metric", dict()).get("type", None) == "md5":
      return f"-f tee -map 0:v '{self.osencoded}|[f=md5]pipe:1'"
    return f"{self.osencoded}"

  @timefn("ffmpeg:encode")
  def encode(self):
    if vars(self).get("_encoded", None) is not None:
      get_media()._purge_test_artifact(self._encoded)
    self._encoded = get_media()._test_artifact2(f"{self.encoded_ext}")

    return call(
      f"{exe2os('ffmpeg')} -v verbose {self.hwinit}"
      f" -f rawvideo -pix_fmt {self.format} -s:v {self.width}x{self.height}"
      f" {self.fps} -i {self.ossource}"
      f" -vf 'format={self.hwformat}{self.hwupload}{self.roi}'"
      f" -an -c:v {self.ffencoder} {self.encparams}"
      f" -vframes {self.frames} -y {self.ffoutput}"
    )

@slash.requires(have_ffmpeg)
class BaseEncoderTest(slash.Test, BaseFormatMapper):
  EncoderClass = Encoder
  DecoderClass = Decoder

  def before(self):
    super().before()
    self.refctx = []
    self.post_validate = lambda: None

  def map_profile(self):
    raise NotImplementedError

  def get_file_ext(self):
    raise NotImplementedError

  def validate_caps(self):
    skip_test_if_missing_features(self)

    if vars(self).get("level", None) is not None:
      self.level /= 10.0

    # FIXME: handle brframes for bitrate rcmodes (see ffmpeg/qsv/encoder.py)
    # May require rebaseline for other components/elements

    self.encoder = self.EncoderClass(encoded_ext = self.get_file_ext(), **vars(self))
    self.decoder = self.DecoderClass(
      caps      = self.caps,
      ffdecoder = vars(self).get("ffdecoder", None),
      frames    = self.frames,
      format    = self.format,
      width     = self.width,
      height    = self.height,
      reference = self.source,
    )

    if None in [self.encoder.hwformat, self.encoder.format, self.decoder.hwformat, self.decoder.format]:
      slash.skip_test("{format} not supported".format(**vars(self)))

    maxw, maxh = self.caps["maxres"]
    if self.width > maxw or self.height > maxh:
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{width}x{height} not supported", **vars(self)))

    if vars(self).get("slices", 1) > 1 and not self.caps.get("multislice", True):
      slash.skip_test(
        format_value(
          "{platform}.{driver}.slice > 1 unsupported in this mode", **vars(self)))

    if not self.caps.get(self.rcmode, True):
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{rcmode} unsupported in this mode", **vars(self)))

    if vars(self).get("profile", None) is not None:
      self.mprofile = self.map_profile()
      if self.mprofile is None:
        slash.skip_test("{profile} profile is not supported".format(**vars(self)))
      self.encoder.update(profile = self.mprofile)

    self.post_validate()

  def _encode_r2r(self):
    assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"

    vars(self).update(metric = dict(type = "md5"))
    self.encoder.update(metric = self.metric)

    metric = metrics2.factory.create(**vars(self))
    metric.actual = parse_inline_md5(self.encoder.encode())
    metric.expect = metric.actual # the first run is our reference for r2r
    metric.check()

    for i in range(1, self.r2r):
      metric.actual = parse_inline_md5(self.encoder.encode())
      metric.check()

  def encode(self):
    self.validate_caps()

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    if vars(self).get("r2r", None) is not None:
      return self._encode_r2r()

    self.output = self.encoder.encode()

    self.check_output()
    self.check_bitrate()
    self.check_level()
    self.check_forced_idr()
    self.check_max_frame_size()
    self.check_metrics()

  def check_output(self):
    pass

  def check_bitrate(self):
    encsize = os.path.getsize(self.encoder.encoded)
    bitrate_actual = encsize * 8 * vars(self).get("fps", 25) / 1024.0 / self.frames
    get_media()._set_test_details(
      size_encoded = encsize,
      bitrate_actual = "{:-.2f}".format(bitrate_actual))

    if "cbr" == self.rcmode:
      bitrate_gap = abs(bitrate_actual - self.bitrate) / self.bitrate
      get_media()._set_test_details(bitrate_gap = "{:.2%}".format(bitrate_gap))

      # acceptable bitrate within 10% of bitrate
      assert(bitrate_gap <= 0.10)

    elif "vbr" == self.rcmode and vars(self).get("maxframesize", None) is None:
      # acceptable bitrate within 25% of minrate and 10% of maxrate
      assert(self.minrate * 0.75 <= bitrate_actual <= self.maxrate * 1.10)

  def check_metrics(self):
    vars(self).update(metric = dict(type = "psnr"))
    self.decoder.update(source = self.encoder.encoded, metric = self.metric)
    self.decoder.decode()

    metric = metrics2.factory.create(**vars(self))
    metric.actual = parse_psnr_stats(self.decoder.statsfile, self.frames)

    metric.check()

  def check_level(self):
    if vars(self).get("level", None) is None:
      return

    output = call(
      f"{exe2os('ffprobe')}"
      f" -i {self.encoder.osencoded} -v quiet -show_entries stream=level"
      f" -of default=nk=1:nw=1"
    )
    assert float(output)/30 == self.level, "fail to set target level"

  def check_forced_idr(self):
    if vars(self).get("vforced_idr", None) is None:
      return

    judge = {"hevc-8" : 19, "avc" : 5}.get(self.codec, None)
    assert judge is not None, f"{self.codec} codec not supported for forced_idr"

    output = call(
      f"{exe2os('ffmpeg')}"
      f" -v verbose -i {self.encoder.osencoded} -c:v copy -bsf:v trace_headers"
      f" -f null - 2>&1 | grep 'nal_unit_type.*{judge}' | wc -l"
    )
    assert str(self.frames) == output.strip(), "It appears that the forced_idr did not work"

  def check_max_frame_size(self):
    if vars(self).get("maxframesize", None) is None:
      return

    output = call(
      f"{exe2os('ffprobe')}"
      f" -i {self.encoder.osencoded} -show_frames | grep pkt_size"
    )
    frameSizes = re.findall(r'(?<=pkt_size=).[0-9]*', output)
    for frameSize in frameSizes:
      assert (self.maxframesize * 1000) >= int(frameSize), "It appears that the max_frame_size did not work"
