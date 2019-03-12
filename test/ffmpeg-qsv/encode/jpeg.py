###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .encoder import EncoderTest

spec = load_test_spec("jpeg", "encode")

class JPEGEncoderTest(EncoderTest):
  def before(self):
    vars(self).update(
      codec     = "jpeg",
      ffencoder = "mjpeg_qsv",
      ffdecoder = "mjpeg_qsv",
      hwformat  = "nv12",
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
  @platform_tags(JPEG_ENCODE_PLATFORMS)
  @slash.requires(have_ffmpeg_mjpeg_qsv_encode)
  ## NOTE: Temporary Workaround for qsv mjpeg encode test until
  ## a qsv mjpeg decoder is available.
  @slash.requires(have_ffmpeg_vaapi_accel)
  #@slash.requires(have_ffmpeg_mjpeg_qsv_decode)
  @slash.parametrize(*gen_jpeg_cqp_parameters(spec))
  def test(self, case, quality):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case    = case,
      quality = quality,
      rcmode  = "cqp",
    )
    self.encode()

  ## NOTE: Temporary Workaround for qsv mjpeg encode test until
  ## a qsv mjpeg decoder is available.
  def check_metrics(self):
    self.decoded = get_media()._test_artifact(
      "{}-{width}x{height}-{format}.yuv".format(self.gen_name(), **vars(self)))

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
