###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("avc", "encode")

def check_output(output, rcmode, gop, slices, bframes, lowpower, profile):

  ipbmode = 0 if gop <= 1 else 1 if bframes < 1 else 2

  ipbmsgs = [
    "Using intra frames only",
    "Using intra and P-frames",
    "Using intra, P- and B-frames"
  ]
  profilemsgs = {
    "high"                  :
      "Using VAAPI profile VAProfileH264High ([0-9]*)",
    "main"                  :
      "Using VAAPI profile VAProfileH264Main ([0-9]*)",
    "constrained-baseline"  :
      "Using VAAPI profile VAProfileH264ConstrainedBaseline ([0-9]*)",
  }
  rcmsgs = dict(
    cqp = "Using constant-quality mode|RC mode: CQP",
    cbr = "RC mode: CBR",
    vbr = "RC mode: VBR",
  )
  entrypointmsgs = [
    "Using VAAPI entrypoint VAEntrypointEncSlice ([0-9]*)",
    "Using VAAPI entrypoint VAEntrypointEncSliceLP ([0-9]*)",
  ]

  m = re.search(profilemsgs[profile], output, re.MULTILINE)
  assert m is not None, "Possible incorrect profile used"

  m = re.search(rcmsgs[rcmode], output, re.MULTILINE)
  assert m is not None, "Possible incorrect RC mode used"

  m = re.search(ipbmsgs[ipbmode], output, re.MULTILINE)
  assert m is not None, "Possible incorrect IPB mode used"

  m = re.search(entrypointmsgs[lowpower], output, re.MULTILINE)
  assert m is not None, "Possible incorrect entrypoint used"

def check_psnr(params):
  call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -i {encoded} -pix_fmt {mformat} -f rawvideo -vsync passthrough"
    " -vframes {frames} -y {decoded}".format(**params))

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
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(have_ffmpeg_h264_vaapi_encode)
@slash.parametrize(*gen_avc_cqp_parameters(spec, ['high', 'main']))
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

  output = call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    " -i {source} -vf 'format=nv12,hwupload' -c:v h264_vaapi"
    " -profile:v {profile} -g {gop} -qp {qp} -bf {bframes} -quality {quality}"
    " -slices {slices} -vframes {frames} -y {encoded}".format(**params))

  check_output(output, "cqp", gop, slices, bframes, 0, profile)

  check_psnr(params)

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(have_ffmpeg_h264_vaapi_encode)
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

  output = call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    " -i {source} -vf 'format=nv12,hwupload' -c:v h264_vaapi -low_power 1"
    " -profile:v {profile} -g {gop} -qp {qp} -quality {quality}"
    " -slices {slices} -vframes {frames} -y {encoded}".format(**params))

  check_output(output, "cqp", gop, slices, 0, 1, profile)

  check_psnr(params)


#-------------------------------------------------#
#---------------------- CBR ----------------------#
#-------------------------------------------------#
@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(have_ffmpeg_h264_vaapi_encode)
@slash.parametrize(*gen_avc_cbr_parameters(spec, ['main', 'high']))
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

  output = call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -r:v {fps}"
    " -i {source} -vf 'format=nv12,hwupload' -c:v h264_vaapi"
    " -profile:v {profile} -g {gop} -bf {bframes} -slices {slices}"
    " -b:v {bitrate}k -maxrate {bitrate}k"
    " -vframes {frames} -y {encoded}".format(**params))

  check_output(output, "cbr", gop, slices, bframes, 0, profile)

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
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(have_ffmpeg_h264_vaapi_encode)
@slash.parametrize(*gen_avc_vbr_parameters(spec, ['main', 'high']))
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
    profile = mprofile, fps = fps, bitrate = bitrate, gop = gop, quality=quality,
    slices = slices, bframes = bframes, refs = refs, minrate = minrate,
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

  output = call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -r:v {fps}"
    " -i {source} -vf 'format=nv12,hwupload' -c:v h264_vaapi"
    " -profile:v {profile} -g {gop} -bf {bframes} -slices {slices}"
    " -b:v {minrate}k -maxrate {maxrate}k -vframes {frames}"
    " -refs {refs} -quality {quality}"
    " -y {encoded}".format(**params))

  check_output(output, "vbr", gop, slices, bframes, 0, profile)

  # calculate actual bitrate
  encsize = os.path.getsize(params["encoded"])
  bitrate_actual = encsize * 8 * params["fps"] / 1024.0 / params["frames"]

  get_media()._set_test_details(
    size_encoded = encsize,
    bitrate_actual = "{:-.2f}".format(bitrate_actual))

  # acceptable bitrate within 25% of minrate and 10% of maxrate
  assert(minrate * 0.75 <= bitrate_actual <= maxrate * 1.10)

  check_psnr(params)
