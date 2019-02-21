###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("mpeg2", "encode")

def check_psnr(params):
  call(
    "ffmpeg -hwaccel qsv -hwaccel_device /dev/dri/renderD128 -v verbose"
    " -c:v mpeg2_qsv -i {encoded} -vf 'hwdownload,format=nv12'"
    " -pix_fmt {mformat} -f rawvideo -vsync passthrough -vframes {frames}"
    " -y {decoded}".format(**params))

  get_media().baseline.check_psnr(
    psnr = calculate_psnr(
      params["source"], params["decoded"],
      params["width"], params["height"],
      params["frames"], params["format"]),
    context = params.get("refctx", []),
  )

#-------------------------------------------------#
#---------------------- CQP ----------------------#
#-------------------------------------------------#
@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(have_ffmpeg_mpeg2_qsv_encode)
@slash.requires(have_ffmpeg_mpeg2_qsv_decode)
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_mpeg2_cqp_parameters(spec, ['main', 'simple']))
@platform_tags(MPEG2_ENCODE_PLATFORMS)
def test_cqp(case, gop, bframes, qp, quality, profile):
  params = spec[case].copy()

  mprofile = mapprofile("mpeg2", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    profile = mprofile, gop = gop, bframes = bframes,
    qp = qp, mqp = mapRange(qp, [0, 100], [1, 51]),
    quality = quality, mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{bframes}-{qp}-{quality}-{profile}"
    ".m2v".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{bframes}-{qp}-{quality}-{profile}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  call(
    "ffmpeg -init_hw_device qsv=qsv:hw -hwaccel qsv -filter_hw_device qsv"
    " -v verbose -f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    " -i {source} -vf 'format=nv12,hwupload=extra_hw_frames=64' -an"
    " -c:v mpeg2_qsv -profile:v {profile} -g {gop} -bf {bframes}"
    " -q {mqp} -preset {quality} -vframes {frames}"
    " -y {encoded}".format(**params))

  check_psnr(params)
