###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

spec      = load_test_spec("jpeg", "encode")
spec_r2r  = load_test_spec("jpeg", "encode", "r2r")

class JPEGEncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec     = "jpeg",
      ffencoder = "mjpeg_qsv",
      ffdecoder = "mjpeg_qsv",
      profile   = "baseline",
    )
    super(JPEGEncoderTest, self).before()

  def get_file_ext(self):
    return "mjpeg" if self.frames > 1 else "jpg"

## NOTE: Temporary Workaround for qsv mjpeg encode test until
## a qsv mjpeg decoder is available.
@memoize
def have_ffmpeg_vaapi_accel():
  return try_call("ffmpeg -hide_banner -hwaccels | grep vaapi")

class cqp(JPEGEncoderTest):
  def init(self, tspec, case, quality):
    self.caps = platform.get_caps("vdenc", "jpeg")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case    = case,
      quality = quality,
      rcmode  = "cqp",
    )

  @slash.requires(*platform.have_caps("vdenc", "jpeg"))
  @slash.requires(*have_ffmpeg_encoder("mjpeg_qsv"))
  ## NOTE: Temporary Workaround for qsv mjpeg encode test until
  ## a qsv mjpeg decoder is available.
  @slash.requires(have_ffmpeg_vaapi_accel)
  #@slash.requires(have_ffmpeg_mjpeg_qsv_decode)
  @slash.parametrize(*gen_jpeg_cqp_parameters(spec))
  def test(self, case, quality):
    self.init(spec, case, quality)
    self.encode()

  @slash.requires(*platform.have_caps("vdenc", "jpeg"))
  @slash.requires(*have_ffmpeg_encoder("mjpeg_qsv"))
  ## NOTE: Temporary Workaround for qsv mjpeg encode test until
  ## a qsv mjpeg decoder is available.
  @slash.requires(have_ffmpeg_vaapi_accel)
  #@slash.requires(have_ffmpeg_mjpeg_qsv_decode)
  @slash.parametrize(*gen_jpeg_cqp_parameters(spec_r2r))
  def test_r2r(self, case, quality):
    self.init(spec_r2r, case, quality)
    vars(self).setdefault("r2r", 5)
    self.encode()

  ## NOTE: Temporary Workaround for qsv mjpeg encode test until
  ## a qsv mjpeg decoder is available.
  def check_metrics(self):
    name = self.gen_name().format(**vars(self))
    self.decoded = get_media()._test_artifact(
      "{}-{width}x{height}-{format}.yuv".format(name, **vars(self)))

    call(
      "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
      " -i {encoded} -pix_fmt {mformat} -f rawvideo -vsync passthrough"
      " -vframes {frames} -y {decoded}".format(**vars(self)))

    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.source, self.decoded,
        self.width, self.height,
        self.frames, self.format),
      context = self.refctx,
    )
