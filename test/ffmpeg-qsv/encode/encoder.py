###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(using_compatible_driver)
class EncoderTest(slash.Test):
  def gen_input_opts(self):
    opts = "-f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"

    if vars(self).get("fps", None) is not None:
      opts += " -r:v {fps}"

    opts += " -i {source}"

    return opts

  def gen_output_opts(self):
    opts = "-vf 'format={hwformat},hwupload=extra_hw_frames=120' -an"
    opts += " -c:v {ffencoder}"

    if self.codec not in ["jpeg",]:
      opts += " -profile:v {mprofile}"

    if vars(self).get("gop", None) is not None:
      opts += " -g {gop}"
    if vars(self).get("qp", None) is not None:
      if self.codec in ["mpeg2"]:
        opts += " -q {mqp}"
      else:
        opts += " -q {qp}"
    if vars(self).get("quality", None) is not None:
      if self.codec in ["jpeg",]:
        opts += " -global_quality {quality}"
      else:
        opts += " -preset {quality}"
    if vars(self).get("slices", None) is not None:
      opts += " -slices {slices}"
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
    if vars(self).get("ladepth", None) is not None:
      opts += " -look_ahead 1"
      opts += " -look_ahead_depth {ladepth}"

    opts += " -vframes {frames} -y {encoded}"

    return opts

  def gen_name(self):
    name = "{case}-{rcmode}-{profile}"
    if vars(self).get("fps", None) is not None:
      name += "-{fps}"
    if vars(self).get("gop", None) is not None:
      name += "-{gop}"
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
    if vars(self).get("ladepth", None) is not None:
      name += "-{ladepth}"
    if vars(self).get("r2r", None) is not None:
      name += "-r2r"

    return name

  def before(self):
    self.refctx = []

  @timefn("ffmpeg")
  def call_ffmpeg(self, iopts, oopts):
    self.output = call(
      "ffmpeg -init_hw_device qsv=qsv:hw -hwaccel qsv -filter_hw_device qsv"
      " -v verbose {iopts} {oopts}".format(iopts = iopts, oopts = oopts))

  def validate_caps(self):
    self.hwformat = match_best_format(self.format, self.caps["fmts"])
    if self.hwformat is None:
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{format} not supported", **vars(self)))

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

    self.mprofile = mapprofile(self.codec, self.profile)
    if self.mprofile is None:
      slash.skip_test("{profile} profile is not supported".format(**vars(self)))

    self.mformat = mapformat(self.format)
    if self.mformat is None:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    self.hwformat = mapformat(self.hwformat)

  def encode(self):
    self.validate_caps()

    iopts = self.gen_input_opts()
    oopts = self.gen_output_opts()
    name  = self.gen_name().format(**vars(self))
    ext   = self.get_file_ext()

    self.encoded = get_media()._test_artifact("{}.{}".format(name, ext))
    self.call_ffmpeg(iopts.format(**vars(self)), oopts.format(**vars(self)))

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = md5(self.encoded)
      get_media()._set_test_details(md5_ref = md5ref)
      for i in xrange(1, self.r2r):
        self.encoded = get_media()._test_artifact("{}_{}.{}".format(name, i, ext))
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

  def check_output(self):
    m = re.search("Initialize MFX session", self.output, re.MULTILINE)
    assert m is not None, "It appears that the QSV plugin did not load"

    if vars(self).get("ladepth", None) is not None:
      m = re.search("Using the VBR with lookahead \(LA\) ratecontrol method", self.output, re.MULTILINE)
      assert m is not None, "It appears that the lookahead did not load"

  def check_metrics(self):
    iopts = "-c:v {ffdecoder} -i {encoded}"
    oopts = (
      "-vf 'hwdownload,format={hwformat}' -pix_fmt {mformat} -f rawvideo"
      " -vsync passthrough -vframes {frames} -y {decoded}")
    name = (self.gen_name() + "-{width}x{height}-{format}").format(**vars(self))

    self.decoded = get_media()._test_artifact("{}.yuv".format(name))
    self.call_ffmpeg(iopts.format(**vars(self)), oopts.format(**vars(self)))

    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.source, self.decoded,
        self.width, self.height,
        self.frames, self.format),
      context = self.refctx,
    )

  def check_bitrate(self):
    if "cbr" == self.rcmode:
      encsize = os.path.getsize(self.encoded)
      bitrate_actual = encsize * 8 * self.fps / 1024.0 / self.frames
      bitrate_gap = abs(bitrate_actual - self.bitrate) / self.bitrate

      get_media()._set_test_details(
        size_encoded = encsize,
        bitrate_actual = "{:-.2f}".format(bitrate_actual),
        bitrate_gap = "{:.2%}".format(bitrate_gap))

      # acceptable bitrate within 10% of bitrate
      assert(bitrate_gap <= 0.10)

    elif "vbr" == self.rcmode:
      encsize = os.path.getsize(self.encoded)
      bitrate_actual = encsize * 8 * self.fps / 1024.0 / self.frames

      get_media()._set_test_details(
        size_encoded = encsize,
        bitrate_actual = "{:-.2f}".format(bitrate_actual))

      # acceptable bitrate within 25% of minrate and 10% of maxrate
      assert(self.minrate * 0.75 <= bitrate_actual <= self.maxrate * 1.10)
