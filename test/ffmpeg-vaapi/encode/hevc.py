###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec8   = load_test_spec("hevc", "encode", "8bit")
spec10  = load_test_spec("hevc", "encode", "10bit")

def check_output(output, rcmode, gop, slices, bframes, profile):

  ipbmode = 0 if gop <= 1 else 1 if bframes < 1 else 2

  ipbmsgs = [
    "Using intra frames only",
    "Using intra and P-frames",
    "Using intra, P- and B-frames"
  ]
  profilemsgs = dict(
    main = "Using VAAPI profile VAProfileHEVCMain ([0-9]*)",
    main10 = "Using VAAPI profile VAProfileHEVCMain10 ([0-9]*)",
  )
  rcmsgs = dict(
    cqp = "Using constant-quality mode|RC mode: CQP",
    cbr = "RC mode: CBR",
    vbr = "RC mode: VBR",
  )

  m = re.search(profilemsgs[profile], output, re.MULTILINE)
  assert m is not None, "Possible incorrect profile used"

  m = re.search(rcmsgs[rcmode], output, re.MULTILINE)
  assert m is not None, "Possible incorrect RC mode used"

  m = re.search(ipbmsgs[ipbmode], output, re.MULTILINE)
  assert m is not None, "Possible incorrect IPB mode used"

def check_bitrate(params):
  # calculate actual bitrate
  encsize = os.path.getsize(params["encoded"])
  bitrate_actual = encsize * 8 * params["fps"] / 1024.0 / params["frames"]
  bitrate_gap = abs(bitrate_actual - params["bitrate"]) / params["bitrate"]

  get_media()._set_test_details(
    size_encoded = encsize,
    bitrate_actual = "{:-.2f}".format(bitrate_actual),
    bitrate_gap = "{:.2%}".format(bitrate_gap))

  assert(bitrate_gap <= 0.10)

def check_bitrate_vbr(params):
  # calculate actual bitrate
  encsize = os.path.getsize(params["encoded"])
  bitrate_actual = encsize * 8 * params["fps"] / 1024.0 / params["frames"]

  get_media()._set_test_details(
    size_encoded = encsize,
    bitrate_actual = "{:-.2f}".format(bitrate_actual))

  # acceptable bitrate within 25% of minrate and 10% of maxrate
  assert(params["minrate"] * 0.75 <= bitrate_actual <= params["maxrate"] * 1.10)

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
#-------------------- CQP 8 ----------------------#
#-------------------------------------------------#
@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(have_ffmpeg_hevc_vaapi_encode)
@slash.parametrize(*gen_hevc_cqp_parameters(spec8, ['main']))
@platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
def test_8bit_cqp(case, gop, slices, bframes, qp, quality, profile):
  params = spec8[case].copy()

  mprofile = mapprofile("hevc-8", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    profile = mprofile, gop = gop, slices = slices, bframes = bframes, qp = qp,
    quality = quality, mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}"
    ".h265".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")

  output = call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    " -i {source} -vf 'format=nv12,hwupload' -c:v hevc_vaapi"
    " -profile:v {profile} -g {gop} -qp {qp} -bf {bframes}"
    " -slices {slices} -vframes {frames} -y {encoded}".format(**params))

  check_output(output, "cqp", gop, slices, bframes, profile)

  check_psnr(params)

#-------------------------------------------------#
#-------------------- CBR 8 ----------------------#
#-------------------------------------------------#
@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(have_ffmpeg_hevc_vaapi_encode)
@slash.parametrize(*gen_hevc_cbr_parameters(spec8, ['main']))
@platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
def test_8bit_cbr(case, gop, slices, bframes, bitrate, fps, profile):
  params = spec8[case].copy()

  mprofile = mapprofile("hevc-8", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    profile = mprofile, fps = fps, bitrate = bitrate, gop = gop,
    slices = slices, bframes = bframes, mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{profile}-{bitrate}-{gop}-{slices}-{bframes}-{fps}"
    ".h265".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{profile}-{bitrate}-{gop}-{slices}-{bframes}-{fps}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  output = call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -r:v {fps}"
    " -i {source} -vf 'format=nv12,hwupload' -c:v hevc_vaapi"
    " -profile:v {profile} -g {gop} -bf {bframes} -slices {slices}"
    " -b:v {bitrate}k -maxrate {bitrate}k"
    " -vframes {frames} -y {encoded}".format(**params))

  check_output(output, "cbr", gop, slices, bframes, profile)

  check_bitrate(params)

  check_psnr(params)

#-------------------------------------------------#
#-------------------- VBR 8 ----------------------#
#-------------------------------------------------#
@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(have_ffmpeg_hevc_vaapi_encode)
@slash.parametrize(*gen_hevc_vbr_parameters(spec8, ['main']))
@platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
def test_8bit_vbr(case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
  params = spec8[case].copy()

  mprofile = mapprofile("hevc-8", profile)
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
    ".h265".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{profile}-{bitrate}-{gop}-{slices}-{bframes}-{fps}-{quality}-{refs}"
    "-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")

  output = call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -r:v {fps}"
    " -i {source} -vf 'format=nv12,hwupload' -c:v hevc_vaapi"
    " -profile:v {profile} -g {gop} -bf {bframes} -slices {slices}"
    " -b:v {minrate}k -maxrate {maxrate}k -refs {refs}"
    " -vframes {frames} -y {encoded}".format(**params))

  check_output(output, "vbr", gop, slices, bframes, profile)

  check_bitrate_vbr(params)

  check_psnr(params)

#-------------------------------------------------#
#-------------------- CQP 10 ---------------------#
#-------------------------------------------------#
@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(have_ffmpeg_hevc_vaapi_encode)
@slash.parametrize(*gen_hevc_cqp_parameters(spec10, ['main10']))
@platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
def test_10bit_cqp(case, gop, slices, bframes, qp, quality, profile):
  params = spec10[case].copy()
  params.update(
    mprofile = mapprofile("hevc-10", profile), gop = gop, slices = slices,
    bframes = bframes, qp = qp, profile = profile, quality = quality,
    mformat = mapformat(params["format"]))

  if params["mprofile"] is None:
    slash.skip_test("{profile} profile is not supported".format(**params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}"
    ".h265".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")

  output = call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height}"
    " -i {source} -vf 'hwupload' -c:v hevc_vaapi"
    " -profile:v {mprofile} -g {gop} -qp {qp} -bf {bframes}"
    " -slices {slices} -vframes {frames} -y {encoded}".format(**params))

  check_output(output, "cqp", gop, slices, bframes, profile)

  check_psnr(params)

#-------------------------------------------------#
#-------------------- CBR 10 ---------------------#
#-------------------------------------------------#
@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(have_ffmpeg_hevc_vaapi_encode)
@slash.parametrize(*gen_hevc_cbr_parameters(spec10, ['main10']))
@platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
def test_10bit_cbr(case, gop, slices, bframes, bitrate, fps, profile):
  params = spec10[case].copy()

  params.update(
    mprofile = mapprofile("hevc-10", profile), fps = fps, bitrate = bitrate,
    profile = profile, gop = gop, slices = slices, bframes = bframes,
    mformat = mapformat(params["format"]))

  if params["mprofile"] is None:
    slash.skip_test("{profile} profile is not supported".format(**params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  params["encoded"] = get_media()._test_artifact(
    "{}-{profile}-{bitrate}-{gop}-{slices}-{bframes}-{fps}"
    ".h265".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{profile}-{bitrate}-{gop}-{slices}-{bframes}-{fps}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  output = call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -r:v {fps}"
    " -i {source} -vf 'hwupload' -c:v hevc_vaapi"
    " -profile:v {mprofile} -g {gop} -bf {bframes} -slices {slices}"
    " -b:v {bitrate}k -maxrate {bitrate}k"
    " -vframes {frames} -y {encoded}".format(**params))

  check_output(output, "cbr", gop, slices, bframes, profile)

  check_bitrate(params)

  check_psnr(params)

#-------------------------------------------------#
#-------------------- VBR 10 ---------------------#
#-------------------------------------------------#
@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(have_ffmpeg_hevc_vaapi_encode)
@slash.parametrize(*gen_hevc_vbr_parameters(spec10, ['main10']))
@platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
def test_10bit_vbr(case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
  params = spec10[case].copy()

  # target percentage 50%
  minrate = bitrate
  maxrate = bitrate * 2

  params.update(
    mprofile = mapprofile("hevc-10", profile), fps = fps, bitrate = bitrate,
    profile = profile, gop = gop, slices = slices, bframes = bframes,
    refs = refs, quality = quality, minrate = minrate, maxrate = maxrate,
    mformat = mapformat(params["format"]))

  if params["mprofile"] is None:
    slash.skip_test("{profile} profile is not supported".format(**params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  params["encoded"] = get_media()._test_artifact(
    "{}-{profile}-{bitrate}-{gop}-{slices}-{bframes}-{fps}-{quality}-{refs}"
    ".h265".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{profile}-{bitrate}-{gop}-{slices}-{bframes}-{fps}-{quality}-{refs}"
    "-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")

  output = call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -r:v {fps}"
    " -i {source} -vf 'hwupload' -c:v hevc_vaapi"
    " -profile:v {mprofile} -g {gop} -bf {bframes} -slices {slices}"
    " -b:v {minrate}k -maxrate {maxrate}k -refs {refs}"
    " -vframes {frames} -y {encoded}".format(**params))

  check_output(output, "vbr", gop, slices, bframes, profile)

  check_bitrate_vbr(params)

  check_psnr(params)
