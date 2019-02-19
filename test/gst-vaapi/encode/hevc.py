###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec8 = load_test_spec("hevc", "encode", "8bit")
spec10 = load_test_spec("hevc", "encode", "10bit")

def check_psnr(params):
  call(
    "gst-launch-1.0 -vf filesrc location={encoded}"
    " ! h265parse ! vaapih265dec"
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

def check_bitrate_vbr(params):
  # calculate actual bitrate
  encsize = os.path.getsize(params["encoded"])
  bitrate_actual = encsize * 8 * params["fps"] / 1024.0 / params["frames"]

  get_media()._set_test_details(
    size_encoded = encsize,
    bitrate_actual = "{:-.2f}".format(bitrate_actual))

  # acceptable bitrate within 25% of minrate and 10% of maxrate
  assert(params["minrate"] * 0.75 <= bitrate_actual <= params["maxrate"] * 1.10)

#-------------------------------------------------#
#--------------------- CQP 8 ---------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapih265enc"))
@slash.requires(*have_gst_element("vaapih265dec"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_hevc_cqp_parameters(spec8, ['main']))
@platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
def test_8bit_cqp(case, gop, slices, bframes, qp, quality, profile):
  params = spec8[case].copy()

  mprofile = mapprofile("hevc-8", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    gop = gop, slices = slices, bframes = bframes, qp = qp, quality = quality,
    profile = mprofile, mformat = mapformat(params["format"]),
    hwup_format = mapformat_hwup(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}"
    ".h265".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! videoconvert ! video/x-raw,format={hwup_format}"
    " ! vaapih265enc rate-control=cqp init-qp={qp} quality-level={quality}"
    " keyframe-period={gop} num-slices={slices} max-bframes={bframes}"
    " ! video/x-h265,profile={profile} ! h265parse"
    " ! filesink location={encoded}".format(**params))

  check_psnr(params)

#-------------------------------------------------#
#--------------------- CBR 8 ---------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapih265enc"))
@slash.requires(*have_gst_element("vaapih265dec"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_hevc_cbr_parameters(spec8, ['main']))
@platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
def test_8bit_cbr(case, gop, slices, bframes, bitrate, fps, profile):
  params = spec8[case].copy()

  mprofile = mapprofile("hevc-8", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    gop = gop, slices = slices, bframes = bframes, bitrate = bitrate,
    profile = mprofile, fps = fps, mformat = mapformat(params["format"]),
    hwup_format = mapformat_hwup(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}"
    ".h265".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " framerate={fps} ! videoconvert ! video/x-raw,format={hwup_format}"
    " ! vaapih265enc rate-control=cbr bitrate={bitrate} keyframe-period={gop}"
    " num-slices={slices} max-bframes={bframes}"
    " ! video/x-h265,profile={profile} ! h265parse"
    " ! filesink location={encoded}".format(**params))

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
#--------------------- VBR 8 ---------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapih265enc"))
@slash.requires(*have_gst_element("vaapih265dec"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_hevc_vbr_parameters(spec8, ['main']))
@platform_tags(HEVC_ENCODE_8BIT_PLATFORMS)
def test_8bit_vbr(case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
  params = spec8[case].copy()

  mprofile = mapprofile("hevc-8", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  # target percentage 70% (hard-coded in gst-vaapi)
  # gst-vaapi sets max-bitrate = bitrate and min-bitrate = bitrate * 0.70
  minrate = bitrate
  maxrate = int(bitrate / 0.7)

  params.update(
    gop = gop, slices = slices, bframes = bframes, bitrate = bitrate,
    profile = mprofile, fps = fps, quality = quality, refs = refs,
    minrate = minrate, maxrate = maxrate, mformat = mapformat(params["format"]),
    hwup_format = mapformat_hwup(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}-{quality}-{refs}"
    ".h265".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}-{quality}-{refs}"
    "-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " framerate={fps} ! videoconvert ! video/x-raw,format={hwup_format}"
    " ! vaapih265enc rate-control=vbr bitrate={maxrate} keyframe-period={gop}"
    " num-slices={slices} max-bframes={bframes} refs={refs}"
    " quality-level={quality} ! video/x-h265,profile={profile} ! h265parse"
    " ! filesink location={encoded}".format(**params))

  check_bitrate_vbr(params)

  check_psnr(params)

#-------------------------------------------------#
#--------------------- CQP 10 --------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapih265enc"))
@slash.requires(*have_gst_element("vaapih265dec"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_hevc_cqp_parameters(spec10, ['main10']))
@platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
def test_10bit_cqp(case, gop, slices, bframes, qp, quality, profile):
  params = spec10[case].copy()

  mprofile = mapprofile("hevc-10", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    gop = gop, slices = slices, bframes = bframes, qp = qp, quality = quality,
    profile = mprofile, mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}"
    ".h265".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! vaapih265enc rate-control=cqp init-qp={qp} quality-level={quality}"
    " keyframe-period={gop} num-slices={slices} max-bframes={bframes}"
    " ! video/x-h265,profile={profile} ! h265parse"
    " ! filesink location={encoded}".format(**params))

  check_psnr(params)

#-------------------------------------------------#
#--------------------- CBR 10 --------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapih265enc"))
@slash.requires(*have_gst_element("vaapih265dec"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_hevc_cbr_parameters(spec10, ['main10']))
@platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
def test_10bit_cbr(case, gop, slices, bframes, bitrate, fps, profile):
  params = spec10[case].copy()

  mprofile = mapprofile("hevc-10", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    gop = gop, slices = slices, bframes = bframes, bitrate = bitrate,
    profile = mprofile, fps = fps, mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}"
    ".h265".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " framerate={fps} ! vaapih265enc rate-control=cbr bitrate={bitrate}"
    " keyframe-period={gop} num-slices={slices} max-bframes={bframes}"
    " ! video/x-h265,profile={profile} ! h265parse"
    " ! filesink location={encoded}".format(**params))

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
#--------------------- VBR 10 --------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapih265enc"))
@slash.requires(*have_gst_element("vaapih265dec"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_hevc_vbr_parameters(spec10, ['main10']))
@platform_tags(HEVC_ENCODE_10BIT_PLATFORMS)
def test_10bit_vbr(case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
  params = spec10[case].copy()

  mprofile = mapprofile("hevc-10", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  # target percentage 70% (hard-coded in gst-vaapi)
  # gst-vaapi sets max-bitrate = bitrate and min-bitrate = bitrate * 0.70
  minrate = bitrate
  maxrate = int(bitrate / 0.7)

  params.update(
    gop = gop, slices = slices, bframes = bframes, bitrate = bitrate,
    profile = mprofile, fps = fps, quality = quality, refs = refs,
    minrate = minrate, maxrate = maxrate, mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}-{quality}-{refs}"
    ".h265".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}-{quality}-{refs}"
    "-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " framerate={fps} ! vaapih265enc rate-control=vbr bitrate={maxrate}"
    " keyframe-period={gop} num-slices={slices} max-bframes={bframes}"
    " refs={refs} quality-level={quality} ! video/x-h265,profile={profile}"
    " ! h265parse ! filesink location={encoded}".format(**params))

  check_bitrate_vbr(params)

  check_psnr(params)
