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
from ...lib.parameters import format_value
from ...lib.util import skip_test_if_missing_features
from ...lib.metrics import md5, calculate_psnr

@slash.requires(have_ffmpeg)
class BaseEncoderTest(slash.Test, BaseFormatMapper):
  def before(self):
    super().before()
    self.refctx = []
    self.renderDevice = get_media().render_device
    self.post_validate = lambda: None

  def map_profile(self):
    raise NotImplementedError

  def gen_qp_opts(self):
    raise NotImplementedError

  def gen_quality_opts(self):
    raise NotImplementedError

  def get_file_ext(self):
    raise NotImplementedError

  def gen_input_opts(self):
    opts = "-f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    if vars(self).get("fps", None) is not None:
      opts += " -r:v {fps}"
    opts += f" -i {filepath2os(self.source)}"
    return opts

  def gen_output_opts(self):
    opts = "-vf 'format={hwformat},hwupload"
    if vars(self).get("hwframes", None) is not None:
      opts += "=extra_hw_frames={hwframes}"
    opts += "' -an -c:v {ffencoder}"

    if vars(self).get("profile", None) is not None:
      opts += " -profile:v {mprofile}"
    if vars(self).get("rcmodeu", None) is not None:
      opts += " -rc_mode {rcmodeu}"
    if vars(self).get("qp", None) is not None:
      opts += self.gen_qp_opts()
    if vars(self).get("quality", None) is not None:
      opts += self.gen_quality_opts()
    if vars(self).get("gop", None) is not None:
      opts += " -g {gop}"
    if vars(self).get("extbrc", None) is not None:
      opts += " -extbrc {extbrc}"
    if vars(self).get("slices", None) is not None:
      opts += " -slices {slices}"
    if vars(self).get("tilecols", None) is not None:
      opts += " -tile_cols {tilecols}"
    if vars(self).get("tilerows", None) is not None:
      opts += " -tile_rows {tilerows}"
    if vars(self).get("bframes", None) is not None:
      opts += " -bf {bframes}"
    if vars(self).get("minrate", None) is not None:
      opts += " -b:v {minrate}k"
    if vars(self).get("maxrate", None) is not None:
      opts += " -maxrate {maxrate}k"
    if vars(self).get("refs", None) is not None:
      opts += " -refs {refs}"
    if vars(self).get("lowpower", None) is not None:
      opts += " -low_power {lowpower}"
    if vars(self).get("loopshp", None) is not None:
      opts += " -loop_filter_sharpness {loopshp}"
    if vars(self).get("looplvl", None) is not None:
      opts += " -loop_filter_level {looplvl}"
    if vars(self).get("level", None) is not None:
      self.level /= 10.0
      opts += " -level {level}"
    if vars(self).get("ladepth", None) is not None:
      opts += " -look_ahead 1"
      opts += " -look_ahead_depth {ladepth}"
    if vars(self).get("vforced_idr", None) is not None:
      opts += " -force_key_frames expr:1 -forced_idr 1"
    if vars(self).get("maxFrameSize", None) is not None:
      opts += " -max_frame_size {maxFrameSize}k"

    # WA: LDB is not enabled by default for HEVCe on gen11+, yet.
    if get_media()._get_gpu_gen() >= 11 and self.codec.startswith("hevc"):
      opts += " -b_strategy 1"

    opts += " -vframes {frames} -y {osencoded}"

    return opts

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
    if vars(self).get("r2r", None) is not None:
      name += "-r2r"

    return name

  def validate_caps(self):
    ifmts = self.caps["fmts"]

    ## BUG: It appears there's a ffmpeg bug with yuv420p hwupload when using
    ## i965 driver.  Need to report upstream ffmpeg!
    if "i965" == get_media()._get_driver_name():
      ifmts = list(set(ifmts) - set(["I420"]))

    self.hwformat = self.map_best_hw_format(self.format, ifmts)
    self.mformat = self.map_format(self.format)
    if None in [self.hwformat, self.mformat]:
      slash.skip_test("{format} not supported".format(**vars(self)))

    skip_test_if_missing_features(self)

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

    self.post_validate()

  @timefn("ffmpeg")
  def call_ffmpeg(self, iopts, oopts):
    return call(
      (
        f"{exe2os('ffmpeg')}"
        " -hwaccel {hwaccel} -init_hw_device {hwaccel}=hw:{renderDevice}"
        " -hwaccel_output_format {hwaccel}"
      ).format(**vars(self)) + (
        " -v verbose {iopts} {oopts}"
      ).format(iopts = iopts, oopts = oopts)
    )

  def encode(self):
    self.validate_caps()

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    name  = self.gen_name().format(**vars(self))
    ext   = self.get_file_ext()

    self.encoded = get_media()._test_artifact("{}.{}".format(name, ext))
    self.osencoded = filepath2os(self.encoded)

    iopts = self.gen_input_opts()
    oopts = self.gen_output_opts()

    self.output = self.call_ffmpeg(iopts.format(**vars(self)), oopts.format(**vars(self)))

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = md5(self.encoded)
      get_media()._set_test_details(md5_ref = md5ref)
      for i in range(1, self.r2r):
        self.encoded = get_media()._test_artifact("{}_{}.{}".format(name, i, ext))
        self.osencoded = filepath2os(self.encoded)
        self.call_ffmpeg(iopts.format(**vars(self)), oopts.format(**vars(self)))
        result = md5(self.encoded)
        get_media()._set_test_details(**{"md5_{:03}".format(i) : result})
        assert result == md5ref, "r2r md5 mismatch"
        # delete encoded file after each iteration
        get_media()._purge_test_artifact(self.encoded)
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
    encsize = os.path.getsize(self.encoded)
    bitrate_actual = encsize * 8 * vars(self).get("fps", 25) / 1024.0 / self.frames
    get_media()._set_test_details(
      size_encoded = encsize,
      bitrate_actual = "{:-.2f}".format(bitrate_actual))

    if "cbr" == self.rcmode:
      bitrate_gap = abs(bitrate_actual - self.bitrate) / self.bitrate
      get_media()._set_test_details(bitrate_gap = "{:.2%}".format(bitrate_gap))

      # acceptable bitrate within 10% of bitrate
      assert(bitrate_gap <= 0.10)

    elif "vbr" == self.rcmode and vars(self).get("maxFrameSize", None) is None:
      # acceptable bitrate within 25% of minrate and 10% of maxrate
      assert(self.minrate * 0.75 <= bitrate_actual <= self.maxrate * 1.10)

  def check_metrics(self):
    iopts = ""
    if vars(self).get("ffdecoder", None) is not None:
      iopts += "-c:v {ffdecoder} "
    iopts += "-i {osencoded}"


    name = (self.gen_name() + "-{width}x{height}-{format}").format(**vars(self))
    self.decoded = get_media()._test_artifact("{}.yuv".format(name))
    oopts = (
      "-vf 'hwdownload,format={hwformat}' -pix_fmt {mformat} -f rawvideo"
      " -vsync passthrough -vframes {frames}"
      f" -y {filepath2os(self.decoded)}")
    self.call_ffmpeg(iopts.format(**vars(self)), oopts.format(**vars(self)))

    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.source, self.decoded,
        self.width, self.height,
        self.frames, self.format),
      context = self.refctx,
    )

  def check_level(self):
    if vars(self).get("level", None) is None:
      return

    output = call(
      f"{exe2os('ffprobe')}"
      " -i {osencoded} -v quiet -show_entries stream=level"
      " -of default=nk=1:nw=1".format(**vars(self)))
    assert float(output)/30 == self.level, "fail to set target level"

  def check_forced_idr(self):
    if vars(self).get("vforced_idr", None) is None:
      return

    judge = {"hevc-8" : 19, "avc" : 5}.get(self.codec, None)
    assert judge is not None, f"{self.codec} codec not supported for forced_idr"

    output = call(
      f"{exe2os('ffmpeg')}"
      " -v verbose -i {osencoded} -c:v copy"
      " -vframes {frames} -bsf:v trace_headers"
      " -f null - 2>&1 | grep 'nal_unit_type.*{judge}' | wc -l".format(**vars(self)))
    assert str(self.frames) == output.strip(), "It appears that the forced_idr did not work"

  def check_max_frame_size(self):
    if vars(self).get("maxFrameSize", None) is None:
      return

    output = call(
      f"{exe2os('ffprobe')}"
      " -i {osencoded} -show_frames | grep pkt_size".format(**vars(self)))
    frameSizes = re.findall(r'(?<=pkt_size=).[0-9]*', output)
    for frameSize in frameSizes:
      assert (self.maxFrameSize * 1000) >= int(frameSize), "It appears that the max_frame_size did not work"
