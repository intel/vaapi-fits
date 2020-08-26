###
### Copyright (C) 2018-2020 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
import re

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(using_compatible_driver)
class EncoderQualityTest(slash.Test):
  def gen_input_opts(self):
    opts = "-f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    if vars(self).get("fps", None) is not None:
      opts += " -r {fps}"
    opts += " -i {source}"
    return opts

  def gen_output_opts(self, bitrate):
    opts = " -c:v {ffencoder}"
    if vars(self).get("profile", None) is not None:
      opts += " -profile:v {mprofile}"
    if vars(self).get("gop", None) is not None:
      opts += " -g {gop}"
    if vars(self).get("quality", None) is not None:
        opts += " -preset {quality}"
    if vars(self).get("bframes", None) is not None:
      opts += " -bf {bframes}"
    opts += " -b:v " + str(bitrate / 1000) + "M"
    opts += " -maxrate " + str((bitrate * 2) / 1000) + "M"
    opts += " -bufsize " + str((bitrate * 4) / 1000) + "M"
    if vars(self).get("refs", None) is not None:
      opts += " -refs {refs}"
    opts += " -extbrc 1 -vframes {frames} -y {encoded}"
    return opts

  def gen_name(self, i):
    name = "quality-{case}-{rcmode}"
    name += format_value("-{platform}",**vars(self))
    if vars(self).get("profile", None) is not None:
      name += "-{profile}"
    if vars(self).get("fps", None) is not None:
      name += "-{fps}"
    if vars(self).get("gop", None) is not None:
      name += "-{gop}"
    if vars(self).get("quality", None) is not None:
      name += "-{quality}"
    if vars(self).get("bframes", None) is not None:
      name += "-{bframes}"
    if vars(self).get("refs", None) is not None:
      name += "-{refs}"
    name += ("-num" + str(i))
    return name

  def before(self):
    self.refctx = []

  @timefn("ffmpeg")
  def call_ffmpeg(self, iopts, oopts):
    self.output = call(
      "ffmpeg {iopts} {oopts}".format(iopts = iopts, oopts = oopts))
  def get_platform(self):
    return format_value("{platform}", **vars(self))

  def validate_caps(self):
    self.hwformat = map_best_hw_format(self.format, self.caps["fmts"])
    self.mformat = mapformat(self.format)
    
    if None in [self.hwformat, self.mformat]:
      slash.skip_test("{format} format not supported".format(**vars(self)))

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
      self.mprofile = mapprofile(self.codec, self.profile)
      if self.mprofile is None:
        slash.skip_test("{profile} profile is not supported".format(**vars(self)))

  def encode(self, bitrate, i):
    list_bitrate_psnr=[]
    self.validate_caps()

    iopts = self.gen_input_opts()
    oopts = self.gen_output_opts(bitrate)
    name  = self.gen_name(i).format(**vars(self))
    ext   = self.get_file_ext()

    self.encoded = get_media()._test_artifact("{}.{}".format(name, ext))
    self.call_ffmpeg(iopts.format(**vars(self)), oopts.format(**vars(self)))

    self.check_bitrate(bitrate)
    list_bitrate_psnr.append([self.get_bitrate(i),self.get_psnr(i)])
    return list_bitrate_psnr

  def check_metrics(self, bitrate1, psnr1, bitrate2, psnr2):
    get_media().baseline.check_bdrate(
      bdrate = calculate_bdrate(
        bitrate1, psnr1,
        bitrate2, psnr2),
      context = self.refctx,
    )

  def get_bitrate(self, i):
    b = (((os.path.getsize("{encoded}".format(**vars(self))) * 8) / int("{frames}".format(**vars(self)))) * int("{fps}".format(**vars(self)))) / 1000
    return round(b, 4)
  
  def get_psnr(self, i):
    name  = self.gen_name(i).format(**vars(self))
    ext_yuv="yuv"
    self.yuv = get_media()._test_artifact("{}.{}".format(name, ext_yuv))
    call("ffmpeg -i {encoded} -y -c:v rawvideo -pix_fmt yuv420p -vsync 0 {yuv}".format(**vars(self)))
    self.psnr = call("psnr {source} {yuv} {width} {height} {frames}".format(**vars(self)))
    return float(self.psnr)

  def check_bitrate(self, bitrate):
    minrate = bitrate
    maxrate = bitrate * 2
    if "vbr" == self.rcmode:
      encsize = os.path.getsize(self.encoded)
      bitrate_actual = encsize * 8 * self.fps / 1024.0 / self.frames
      get_media()._set_test_details(
        size_encoded = encsize,
        bitrate_actual = "{:-.2f}".format(bitrate_actual))

      # acceptable bitrate within 25% of minrate and 10% of maxrate
      assert(minrate * 0.75 <= bitrate_actual <= maxrate * 1.10)
