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
from ...lib.ffmpeg.decoderbase import Decoder
from ...lib.metrics import md5, calculate_psnr
from ...lib.parameters import format_value
from ...lib.properties import PropertyHandler
from ...lib.util import skip_test_if_missing_features

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
  encoded       = property(lambda s: s.props["encoded"])
  osencoded     = property(lambda s: filepath2os(s.encoded))

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
      f"{self.maxframesize}{self.pict}{self.rqp}"
    )

  @timefn("ffmpeg-encode")
  def encode(self):
    return call(
      f"{exe2os('ffmpeg')} -v verbose {self.hwinit}"
      f" -f rawvideo -pix_fmt {self.format} -s:v {self.width}x{self.height}"
      f" {self.fps} -i {self.ossource}"
      f" -vf 'format={self.hwformat}{self.hwupload}{self.roi}'"
      f" -an -c:v {self.ffencoder} {self.encparams}"
      f" -vframes {self.frames} -y {self.osencoded}"
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

  def gen_name(self):
    name = "{case}-{rcmode}"
    if vars(self).get("profile", None) is not None:
      name += "-{profile}"
    if vars(self).get("fps", None) is not None:
      name += "-{fps}"
    if vars(self).get("gop", None) is not None:
      name += "-{gop}"
    if vars(self).get("extbrc", None) is not None:
      name += "-extbrc{extbrc}"
    if vars(self).get("qp", None) is not None:
      name += "-{qp}"
    if vars(self).get("slices", None) is not None:
      name += "-{slices}"
    if vars(self).get("quality", None) is not None:
      name += "-{quality}"
    if vars(self).get("bframes", None) is not None:
      name += "-{bframes}"
    if vars(self).get("minrate", None) is not None:
      name += "-{minrate}k"
    if vars(self).get("maxrate", None) is not None:
      name += "-{maxrate}k"
    if vars(self).get("refs", None) is not None:
      name += "-{refs}"
    if vars(self).get("lowpower", None) is not None:
      name += "-{lowpower}"
    if vars(self).get("loopshp", None) is not None:
      name += "-{loopshp}"
    if vars(self).get("looplvl", None) is not None:
      name += "-{looplvl}"
    if vars(self).get("ladepth", None) is not None:
      name += "-{ladepth}"
    if vars(self).get("vforced_idr", None) is not None:
      name += "-{vforced_idr}"
    if vars(self).get("level", None) is not None:
      name += "-{level}"
    if vars(self).get("intref", None) is not None:
      name += "-intref-{intref[type]}-{intref[size]}-{intref[dist]}"
    if vars(self).get("vpict", None) is not None:
      name += "-pict-0"
    if vars(self).get("roi", None) is not None:
      name += "-roi"
    if vars(self).get("rqp", None) is not None:
      name += "-rqp"
    if vars(self).get("r2r", None) is not None:
      name += "-r2r"

    return name

  def validate_caps(self):
    skip_test_if_missing_features(self)

    if vars(self).get("level", None) is not None:
      self.level /= 10.0

    # FIXME: handle brframes for bitrate rcmodes (see ffmpeg/qsv/encoder.py)
    # May require rebaseline for other components/elements

    self.encoder = self.EncoderClass(**vars(self))
    self.decoder = self.DecoderClass(
      caps      = self.caps,
      ffdecoder = vars(self).get("ffdecoder", None),
      frames    = self.frames,
      format    = self.format,
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

  def encode(self):
    self.validate_caps()

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    name  = self.gen_name().format(**vars(self))
    ext   = self.get_file_ext()

    self.encoder.update(encoded = get_media()._test_artifact(f"{name}.{ext}"))
    self.output = self.encoder.encode()

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = md5(self.encoder.encoded)
      get_media()._set_test_details(md5_ref = md5ref)
      for i in range(1, self.r2r):
        self.encoder.update(encoded = get_media()._test_artifact(f"{name}_{i}.{ext}"))
        self.encoder.encode()
        result = md5(self.encoder.encoded)
        get_media()._set_test_details(**{f"md5_{i:03}" : result})
        assert result == md5ref, "r2r md5 mismatch"
        # delete encoded file after each iteration
        get_media()._purge_test_artifact(self.encoder.encoded)
    else:
      self.check_output()
      self.check_bitrate()
      self.check_metrics()
      self.check_level()
      self.check_forced_idr()
      self.check_max_frame_size()

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
    name = (self.gen_name() + "-{width}x{height}-{format}").format(**vars(self))
    self.decoder.update(
      source  = self.encoder.encoded,
      decoded = get_media()._test_artifact(f"{name}.yuv"),
    )
    self.decoder.decode()

    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.source, self.decoder.decoded,
        self.width, self.height,
        self.frames, self.format),
      context = self.refctx,
    )

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
