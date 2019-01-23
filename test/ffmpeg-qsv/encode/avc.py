###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("avc", "encode")

def check_psnr(params):
  call(
    "ffmpeg -hwaccel qsv -hwaccel_device /dev/dri/renderD128 -v verbose"
    " -c:v h264_qsv -i {encoded} -vf 'hwdownload,format=nv12'"
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
@slash.requires(have_ffmpeg_h264_qsv_encode)
@slash.requires(have_ffmpeg_h264_qsv_decode)
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_avc_cqp_parameters(spec, ['high', 'main', 'baseline']))
@platform_tags(AVC_ENCODE_PLATFORMS)
def test_cqp(case, gop, slices, bframes, qp, quality, profile):
  params = spec[case].copy()

  mprofile = mapprofile("avc", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    profile = mprofile, gop = gop, slices = slices, bframes = bframes, qp = qp,
    quality = quality, mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}"
    ".h264".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  call(
    "ffmpeg -init_hw_device qsv=qsv:hw -hwaccel qsv -filter_hw_device qsv"
    " -v verbose -f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    " -i {source} -vf 'format=nv12,hwupload=extra_hw_frames=64' -an"
    " -c:v h264_qsv -profile:v {profile} -g {gop} -bf {bframes} -slices {slices}"
    " -q {qp} -preset {quality} -vframes {frames}"
    " -y {encoded}".format(**params))

  check_psnr(params)

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(have_ffmpeg_h264_qsv_encode)
@slash.requires(have_ffmpeg_h264_qsv_decode)
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_avc_cqp_lp_parameters(spec, ['high', 'main']))
@platform_tags(AVC_ENCODE_LP_PLATFORMS)
def test_cqp_lp(case, gop, slices, qp, quality, profile):
  params = spec[case].copy()

  mprofile = mapprofile("avc", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    profile = mprofile, gop = gop, slices = slices, qp = qp,
    quality = quality, mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{qp}-{quality}-{profile}"
    ".h264".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{qp}-{quality}-{profile}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  call(
    "ffmpeg -init_hw_device qsv=qsv:hw -hwaccel qsv -filter_hw_device qsv"
    " -v verbose -f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    " -i {source} -vf 'format=nv12,hwupload=extra_hw_frames=64' -an"
    " -c:v h264_qsv -profile:v {profile} -g {gop} -slices {slices}"
    " -q {qp} -preset {quality} -low_power 1 -vframes {frames}"
    " -y {encoded}".format(**params))

  check_psnr(params)

#-------------------------------------------------#
#---------------------- CBR ----------------------#
#-------------------------------------------------#
@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(have_ffmpeg_h264_qsv_encode)
@slash.requires(have_ffmpeg_h264_qsv_decode)
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_avc_cbr_parameters(spec, ["main", "high", "baseline"]))
@platform_tags(AVC_ENCODE_PLATFORMS)
def test_cbr(case, gop, slices, bframes, bitrate, fps, profile):
  params = spec[case].copy()

  mprofile = mapprofile("avc", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    profile = mprofile, fps = fps, bitrate = bitrate, gop = gop,
    slices = slices, bframes = bframes, mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{profile}-{bitrate}-{gop}-{slices}-{bframes}-{fps}"
    ".h264".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{profile}-{bitrate}-{gop}-{slices}-{bframes}-{fps}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  call(
    "ffmpeg -init_hw_device qsv=qsv:hw -hwaccel qsv -filter_hw_device qsv"
    " -v verbose -f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    " -r:v {fps} -i {source} -vf 'format=nv12,hwupload=extra_hw_frames=64' -an"
    " -c:v h264_qsv -profile:v {profile} -g {gop} -bf {bframes} -slices {slices}"
    " -b:v {bitrate}k -maxrate {bitrate}k -vframes {frames}"
    " -y {encoded}".format(**params))

  # calculate actual bitrate
  encsize = os.path.getsize(params["encoded"])
  bitrate_actual = encsize * 8 * params["fps"] / 1024.0 / params["frames"]
  bitrate_gap = abs(bitrate_actual - bitrate) / bitrate

  get_media()._set_test_details(
    size_encoded = encsize,
    bitrate_actual = "{:-.2f}".format(bitrate_actual),
    bitrate_gap = "{:.2%}".format(bitrate_gap))

  assert(bitrate_gap <= 0.10)

  check_psnr(params)


#-------------------------------------------------#
#---------------------- VBR ----------------------#
#-------------------------------------------------#
@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(have_ffmpeg_h264_qsv_encode)
@slash.requires(have_ffmpeg_h264_qsv_decode)
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_avc_vbr_parameters(spec, ["main", "high", "baseline"]))
@platform_tags(AVC_ENCODE_PLATFORMS)
def test_vbr(case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
  params = spec[case].copy()

  mprofile = mapprofile("avc", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  # target percentage 50%
  minrate = bitrate
  maxrate = bitrate * 2

  params.update(
    profile = mprofile, fps = fps, bitrate = bitrate, gop = gop, refs = refs,
    slices = slices, bframes = bframes, quality = quality, minrate = minrate,
    maxrate = maxrate, mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{profile}-{bitrate}-{gop}-{slices}-{bframes}-{fps}-{quality}-{refs}"
    ".h264".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{profile}-{bitrate}-{gop}-{slices}-{bframes}-{fps}-{quality}-{refs}"
    "-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  call(
    "ffmpeg -init_hw_device qsv=qsv:hw -hwaccel qsv -filter_hw_device qsv"
    " -v verbose -f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    " -r:v {fps} -i {source} -vf 'format=nv12,hwupload=extra_hw_frames=64' -an"
    " -c:v h264_qsv -profile:v {profile} -g {gop} -bf {bframes} -slices {slices}"
    " -b:v {minrate}k -maxrate {maxrate}k -vframes {frames}"
    " -refs {refs} -preset {quality}"
    " -y {encoded}".format(**params))

  # calculate actual bitrate
  encsize = os.path.getsize(params["encoded"])
  bitrate_actual = encsize * 8 * params["fps"] / 1024.0 / params["frames"]

  get_media()._set_test_details(
    size_encoded = encsize,
    bitrate_actual = "{:-.2f}".format(bitrate_actual))

  # acceptable bitrate within 25% of minrate and 10% of maxrate
  assert(minrate * 0.75 <= bitrate_actual <= maxrate * 1.10)

  check_psnr(params)
