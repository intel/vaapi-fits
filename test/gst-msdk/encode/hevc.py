###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec8 = load_test_spec("hevc", "encode", "8bit")
spec10 = load_test_spec("hevc", "encode", "10bit")

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
    "gst-launch-1.0 -vf filesrc location={encoded}"
    " ! h265parse ! msdkh265dec hardware=true"
    " ! videoconvert ! video/x-raw,format={mformatu}"
    " ! checksumsink2 file-checksum=false frame-checksum=false"
    " plane-checksum=false dump-output=true qos=false"
    " dump-location={decoded}".format(
      mformatu = mapformatu(params["format"]), **params
    )
  )

  get_media().baseline.check_psnr(
    psnr = calculate_psnr(
      params["source"], params["decoded"],
      params["width"], params["height"],
      params["frames"], params["format"]),
    context = params.get("refctx", []),
  )


def run_cqp(params):
  params["encoded"] = get_media()._test_artifact(
    "{case}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}"
    ".h265".format(**params))
  params["decoded"] = get_media()._test_artifact(
    "{case}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}"
    "-{width}x{height}-{format}"
    ".yuv".format(**params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! msdkh265enc rate-control=cqp qpp={qp} gop-size={gop} num-slices={slices}"
    " b-frames={bframes} target-usage={quality} hardware=true"
    " ! video/x-h265,profile={mprofile} ! h265parse"
    " ! filesink location={encoded}".format(**params))

  check_psnr(params)

def run_cbr(params):
  params["encoded"] = get_media()._test_artifact(
    "{case}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}"
    ".h265".format(**params))
  params["decoded"] = get_media()._test_artifact(
    "{case}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}"
    "-{width}x{height}-{format}"
    ".yuv".format(**params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " framerate={fps}"
    " ! msdkh265enc rate-control=cbr bitrate={bitrate} gop-size={gop}"
    " num-slices={slices} b-frames={bframes} hardware=true"
    " ! video/x-h265,profile={mprofile} ! h265parse"
    " ! filesink location={encoded}".format(**params))

  check_bitrate(params)
  check_psnr(params)

def run_vbr(params):
  params["encoded"] = get_media()._test_artifact(
    "{case}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}-{quality}-{refs}"
    ".h265".format(**params))
  params["decoded"] = get_media()._test_artifact(
    "{case}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}-{quality}-{refs}"
    "-{width}x{height}-{format}"
    ".yuv".format(**params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " framerate={fps} ! msdkh265enc rate-control=vbr bitrate={minrate}"
    " max-vbv-bitrate={maxrate} gop-size={gop}"
    " num-slices={slices} b-frames={bframes} hardware=true"
    " target-usage={quality} ref-frames={refs}"
    " ! video/x-h265,profile={mprofile} ! h265parse"
    " ! filesink location={encoded}".format(**params))

  check_bitrate_vbr(params)
  check_psnr(params)

#-------------------------------------------------#
#---------------------- CQP 8 --------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(have_gst_msdk)
@slash.requires(have_gst_msdkh265enc)
@slash.requires(have_gst_msdkh265dec)
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_hevc_cqp_parameters(spec8, ['main']))
@platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
def test_8bit_cqp(case, gop, slices, bframes, qp, quality, profile):
  params = spec8[case].copy()

  params.update(
    gop = gop, slices = slices, bframes = bframes, qp = qp, quality = quality,
    case = case, profile = profile, mprofile = mapprofile("hevc-8", profile),
    mformat = mapformat(params["format"]))

  if params["mprofile"] is None:
    slash.skip_test("{} profile is not supported".format(profile))

  run_cqp(params)

#-------------------------------------------------#
#---------------------- CBR 8 --------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(have_gst_msdk)
@slash.requires(have_gst_msdkh265enc)
@slash.requires(have_gst_msdkh265dec)
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_hevc_cbr_parameters(spec8, ['main']))
@platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
def test_8bit_cbr(case, gop, slices, bframes, bitrate, fps, profile):
  params = spec8[case].copy()

  params.update(
    gop = gop, slices = slices, bframes = bframes, bitrate = bitrate, fps = fps,
    case = case, profile = profile, mprofile = mapprofile("hevc-8", profile),
    mformat = mapformat(params["format"]))

  if params["mprofile"] is None:
    slash.skip_test("{} profile is not supported".format(profile))

  run_cbr(params)

#-------------------------------------------------#
#---------------------- VBR 8 --------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(have_gst_msdk)
@slash.requires(have_gst_msdkh265enc)
@slash.requires(have_gst_msdkh265dec)
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_hevc_vbr_parameters(spec8, ['main']))
@platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
def test_8bit_vbr(case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
  params = spec8[case].copy()

  # target percentage 50%
  minrate = bitrate
  maxrate = bitrate * 2

  params.update(
    gop = gop, slices = slices, bframes = bframes, bitrate = bitrate, fps = fps,
    case = case, profile = profile, mprofile = mapprofile("hevc-8", profile),
    quality = quality, refs = refs, minrate = minrate, maxrate = maxrate,
    mformat = mapformat(params["format"]))

  if params["mprofile"] is None:
    slash.skip_test("{} profile is not supported".format(profile))

  run_vbr(params)

#-------------------------------------------------#
#--------------------- CQP 10 --------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(have_gst_msdk)
@slash.requires(have_gst_msdkh265enc)
@slash.requires(have_gst_msdkh265dec)
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_hevc_cqp_parameters(spec10, ['main10']))
@platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
def test_10bit_cqp(case, gop, slices, bframes, qp, quality, profile):
  params = spec10[case].copy()

  params.update(
    gop = gop, slices = slices, bframes = bframes, qp = qp, quality = quality,
    case = case, profile = profile, mprofile = mapprofile("hevc-10", profile),
    mformat = mapformat(params["format"]))

  if params["mprofile"] is None:
    slash.skip_test("{} profile is not supported".format(profile))

  run_cqp(params)

#-------------------------------------------------#
#---------------------- CBR 10 --------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(have_gst_msdk)
@slash.requires(have_gst_msdkh265enc)
@slash.requires(have_gst_msdkh265dec)
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_hevc_cbr_parameters(spec10, ['main10']))
@platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
def test_10bit_cbr(case, gop, slices, bframes, bitrate, fps, profile):
  params = spec10[case].copy()

  params.update(
    gop = gop, slices = slices, bframes = bframes, bitrate = bitrate, fps = fps,
    case = case, profile = profile, mprofile = mapprofile("hevc-10", profile),
    mformat = mapformat(params["format"]))

  if params["mprofile"] is None:
    slash.skip_test("{} profile is not supported".format(profile))

  run_cbr(params)

#-------------------------------------------------#
#---------------------- VBR 10 --------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(have_gst_msdk)
@slash.requires(have_gst_msdkh265enc)
@slash.requires(have_gst_msdkh265dec)
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_hevc_vbr_parameters(spec10, ['main10']))
@platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
def test_10bit_vbr(case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
  params = spec10[case].copy()

  # target percentage 50%
  minrate = bitrate
  maxrate = bitrate * 2

  params.update(
    gop = gop, slices = slices, bframes = bframes, bitrate = bitrate, fps = fps,
    case = case, profile = profile, mprofile = mapprofile("hevc-10", profile),
    quality = quality, refs = refs, minrate = minrate, maxrate = maxrate,
    mformat = mapformat(params["format"]))

  if params["mprofile"] is None:
    slash.skip_test("{} profile is not supported".format(profile))

  run_vbr(params)
