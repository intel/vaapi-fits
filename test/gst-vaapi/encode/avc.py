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
    "gst-launch-1.0 -vf filesrc location={encoded}"
    " ! h264parse ! vaapih264dec"
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

#-------------------------------------------------#
#---------------------- CQP ----------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapih264enc"))
@slash.requires(*have_gst_element("vaapih264dec"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_avc_cqp_parameters(spec, ['main', 'high']))
@platform_tags(AVC_ENCODE_PLATFORMS)
def test_cqp(case, gop, slices, bframes, qp, quality, profile):
  params = spec[case].copy()

  mprofile = mapprofile("avc", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    gop = gop, slices = slices, bframes = bframes, qp = qp, quality = quality,
    profile = mprofile, mformat = mapformat(params["format"]),
    hwup_format = mapformat_hwup(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}"
    ".h264".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{qp}-{quality}-{profile}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! videoconvert ! video/x-raw,format={hwup_format}"
    " ! vaapih264enc rate-control=cqp init-qp={qp} quality-level={quality}"
    " keyframe-period={gop} num-slices={slices} max-bframes={bframes}"
    " ! video/x-h264,profile={profile} ! h264parse"
    " ! filesink location={encoded}".format(**params))

  check_psnr(params)

@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapih264enc"))
@slash.requires(*have_gst_element("vaapih264dec"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_avc_cqp_lp_parameters(spec, ['high', 'main']))
@platform_tags(AVC_ENCODE_LP_PLATFORMS)
def test_cqp_lp(case, gop, slices, qp, quality, profile):
  params = spec[case].copy()

  mprofile = mapprofile("avc", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    profile = mprofile, gop = gop, slices = slices, qp = qp,
    quality = quality, mformat = mapformat(params["format"]),
    hwup_format = mapformat_hwup(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{qp}-{quality}-{profile}"
    ".h264".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{qp}-{quality}-{profile}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! videoconvert ! video/x-raw,format={hwup_format}"
    " ! vaapih264enc rate-control=cqp init-qp={qp} quality-level={quality}"
    " keyframe-period={gop} num-slices={slices} tune=low-power"
    " ! video/x-h264,profile={profile} ! h264parse"
    " ! filesink location={encoded}".format(**params))

  check_psnr(params)


#-------------------------------------------------#
#---------------------- CBR ----------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapih264enc"))
@slash.requires(*have_gst_element("vaapih264dec"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_avc_cbr_parameters(spec, ['main', 'high']))
@platform_tags(AVC_ENCODE_PLATFORMS)
def test_cbr(case, gop, slices, bframes, bitrate, fps, profile):
  params = spec[case].copy()

  mprofile = mapprofile("avc", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    gop = gop, slices = slices, bframes = bframes, bitrate = bitrate,
    profile = mprofile, fps = fps, mformat = mapformat(params["format"]),
    hwup_format = mapformat_hwup(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}"
    ".h264".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " framerate={fps} ! videoconvert ! video/x-raw,format={hwup_format}"
    " ! vaapih264enc rate-control=cbr bitrate={bitrate} keyframe-period={gop}"
    " num-slices={slices} max-bframes={bframes}"
    " ! video/x-h264,profile={profile} ! h264parse"
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
#---------------------- VBR ----------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapih264enc"))
@slash.requires(*have_gst_element("vaapih264dec"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_avc_vbr_parameters(spec, ['main', 'high']))
@platform_tags(AVC_ENCODE_PLATFORMS)
def test_vbr(case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
  params = spec[case].copy()

  mprofile = mapprofile("avc", profile)
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
    ".h264".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{slices}-{bframes}-{bitrate}-{profile}-{fps}-{quality}-{refs}"
    "-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " framerate={fps} ! videoconvert ! video/x-raw,format={hwup_format}"
    " ! vaapih264enc rate-control=vbr bitrate={maxrate} keyframe-period={gop}"
    " num-slices={slices} max-bframes={bframes} refs={refs}"
    " quality-level={quality} ! video/x-h264,profile={profile} ! h264parse"
    " ! filesink location={encoded}".format(**params))

  # calculate actual bitrate
  encsize = os.path.getsize(params["encoded"])
  bitrate_actual = encsize * 8 * params["fps"] / 1024.0 / params["frames"]

  get_media()._set_test_details(
    size_encoded = encsize,
    bitrate_actual = "{:-.2f}".format(bitrate_actual))

  # acceptable bitrate within 25% of minrate and 10% of maxrate
  assert(minrate * 0.75 <= bitrate_actual <= maxrate * 1.10)

  check_psnr(params)
