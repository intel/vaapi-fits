###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
class EncoderTest(slash.Test):
  def gen_input_opts(self):
    opts = "-f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"

    if vars(self).get("fps", None) is not None:
      opts += " -r:v {fps}"

    opts += " -i {source}"

    return opts

  def gen_output_opts(self):
    opts = "-vf 'format={hwupfmt},hwupload' -c:v {ffenc}"

    if self.codec not in ["jpeg", "vp8", "vp9",]:
      opts += " -profile:v {mprofile}"

    if self.codec not in ["jpeg",]:
      opts += " -rc_mode {rcmodeu}"

    if vars(self).get("gop", None) is not None:
      opts += " -g {gop}"
    if vars(self).get("qp", None) is not None:
      if self.codec in ["vp8", "vp9",]:
        opts += " -global_quality {qp}"
      elif self.codec in ["mpeg2"]:
        opts += " -global_quality {mqp}"
      else:
        opts += " -qp {qp}"
    if vars(self).get("quality", None) is not None:
      if self.codec in ["jpeg",]:
        opts += " -global_quality {quality}"
      else:
        opts += " -quality {quality}"
    if vars(self).get("slices", None) is not None:
      opts += " -slices {slices}"
    if vars(self).get("bframes", None) is not None:
      opts += " -bf {bframes}"
    if vars(self).get("minrate", None) is not None:
      opts += " -b:v {minrate}k"
    if vars(self).get("maxrate", None) is not None:
      opts += " -maxrate {maxrate}k"
    if vars(self).get("refmode", None) is not None:
      opts += " -refs {refs}"
    if vars(self).get("lowpower", None) is not None:
      opts += " -low_power {lowpower}"
    if vars(self).get("loopshp", None) is not None:
      opts += " -loop_filter_sharpness {loopshp}"
    if vars(self).get("looplvl", None) is not None:
      opts += " -loop_filter_level {looplvl}"

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
    if vars(self).get("refmode", None) is not None:
      name += "-{refs}"
    if vars(self).get("lowpower", None) is not None:
      name += "-{lowpower}"
    if vars(self).get("loopshp", None) is not None:
      name += "-{loopshp}"
    if vars(self).get("looplvl", None) is not None:
      name += "-{looplvl}"
    if vars(self).get("r2r", None) is not None:
      name += "-r2r"

    return name

  def before(self):
    self.refctx = []

  @timefn("ffmpeg")
  def call_ffmpeg(self, iopts, oopts):
    self.output = call(
      "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
      " {iopts} {oopts}".format(iopts = iopts, oopts = oopts))

  def encode(self):
    self.mprofile = mapprofile(self.codec, self.profile)
    if self.mprofile is None:
      slash.skip_test("{profile} profile is not supported".format(**vars(self)))

    self.mformat = mapformat(self.format)
    if self.mformat is None:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    vars(self).update(rcmodeu = self.rcmode.upper())

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
    # profile
    m = re.search(
      "Using VAAPI profile {} ([0-9]*)".format(self.get_vaapi_profile()),
      self.output, re.MULTILINE)
    assert m is not None, "Possible incorrect profile used"

    # entrypoint
    entrypointmsgs = [
      "Using VAAPI entrypoint {} ([0-9]*)".format(
        "VAEntrypointEncSlice" if "jpeg" != self.codec else "VAEntrypointEncPicture"),
      "Using VAAPI entrypoint VAEntrypointEncSliceLP ([0-9]*)",
    ]
    m = re.search(
      entrypointmsgs[vars(self).get("lowpower", 0)], self.output, re.MULTILINE)
    assert m is not None, "Possible incorrect entrypoint used"

    # rate control mode
    rcmsgs = dict(
      cqp = (
        "Using constant-quality mode"
        "|RC mode: CQP"
        "|Driver does not report any supported rate control modes: assuming constant-quality"
      ),
      cbr = "RC mode: CBR",
      vbr = "RC mode: VBR",
    )
    m = re.search(rcmsgs[self.rcmode], self.output, re.MULTILINE)
    assert m is not None, "Possible incorrect RC mode used"

    # ipb mode
    ipbmode = 0 if vars(self).get("gop", 0) <= 1 else 1 if vars(self).get("bframes", 0) < 1 else 2
    ipbmsgs = [
      "Using intra frames only",
      "Using intra and P-frames",
      "Using intra, P- and B-frames"
    ]
    m = re.search(ipbmsgs[ipbmode], self.output, re.MULTILINE)
    assert m is not None, "Possible incorrect IPB mode used"

  def check_metrics(self):
    iopts = "-i {encoded}"
    oopts = (
      "-pix_fmt {mformat} -f rawvideo -vsync passthrough"
      " -vframes {frames} -y {decoded}")
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
