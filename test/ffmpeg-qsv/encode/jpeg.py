###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("jpeg", "encode")

# NOTE: Temporary Workaround for qsv mjpeg encode test until
# a qsv mjpeg decoder is available.
@memoize
def have_ffmpeg_vaapi_accel():
  return try_call("ffmpeg -hide_banner -hwaccels | grep vaapi")

def check_psnr(params):

  # NOTE: Temporary Workaround for qsv mjpeg encode test until
  # a qsv mjpeg decoder is available.
  call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -i {encoded} -pix_fmt {mformat} -f rawvideo -vsync passthrough"
    " -vframes {frames} -y {decoded}".format(**params))
  #call(
    #"ffmpeg -hwaccel qsv -hwaccel_device /dev/dri/renderD128 -v verbose"
    #" -c:v mjpeg_qsv -i {encoded} -pix_fmt {mformat}"
    #" -f rawvideo -vsync passthrough"
    #" -vframes {frames} -y {decoded}".format(**params))

  get_media().baseline.check_psnr(
    psnr = calculate_psnr(
      params["source"], params["decoded"],
      params["width"], params["height"],
      params["frames"], params["format"]),
    context = params.get("refctx", []),
  )

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(have_ffmpeg_mjpeg_qsv_encode)
# NOTE: Temporary Workaround for qsv mjpeg encode test until
# a qsv mjpeg decoder is available.
@slash.requires(have_ffmpeg_vaapi_accel)
#@slash.requires(have_ffmpeg_mjpeg_qsv_decode)
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_jpeg_cqp_parameters(spec))
@platform_tags(JPEG_ENCODE_PLATFORMS)
def test_cqp(case, quality):
  params = spec[case].copy()
  params.update(
    quality = quality, ext = "mjpeg" if params["frames"] > 1 else "jpg",
    mformat = mapformat(params["format"]))
  params["encoded"] = get_media()._test_artifact(
    "{}-{quality}.{ext}".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{quality}-{width}x{height}-{format}.yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  try:
    # FIXME: Temporary workaround for bug in ffmpeg-qsv that causes test to
    # hang.  We need this patch in ffmpeg https://patchwork.ffmpeg.org/patch/10639/
    # to fix the hang.  For now, instead of using the global call timeout of
    # 180 seconds + 60 seconds for call() thread joins.  Let's just force
    # timeout to be 10 seconds.  10 seconds should be plenty for most jpeg
    # encode cases once the patch merges.  Nonetheless, we should remove this
    # WA once the patch merges.
    default_timeout = get_media().call_timeout
    get_media().call_timeout = 10
    call(
      "ffmpeg -init_hw_device qsv=qsv:hw -hwaccel qsv -filter_hw_device qsv"
      " -v verbose -f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
      " -i {source} -vf 'format=nv12,hwupload=extra_hw_frames=64'"
      " -c:v mjpeg_qsv -global_quality {quality}"
      " -vframes {frames} -y {encoded}".format(**params))
  finally:
    get_media().call_timeout = default_timeout

  check_psnr(params)
