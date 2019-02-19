###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vp9", "encode", "8bit")

def check_psnr(params):
  call(
    "gst-launch-1.0 -vf filesrc location={encoded}"
    " ! matroskademux ! vaapivp9dec"
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
@slash.requires(*have_gst_element("vaapivp9enc"))
@slash.requires(*have_gst_element("vaapivp9dec"))
@slash.parametrize(*gen_vp9_cqp_parameters(spec))
@platform_tags(VP9_ENCODE_8BIT_PLATFORMS)
def test_8bit_cqp(case, ipmode, qp, quality, refmode, looplvl, loopshp):
  params = spec[case].copy()

  params.update(
    ipmode = ipmode, qp = qp, quality = quality, looplvl = looplvl,
    gop = 30 if ipmode != 0 else 1, refmode = refmode,
    loopshp = loopshp, mformat = mapformat(params["format"]),
    hwup_format = mapformat_hwup(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{ipmode}-{qp}-{quality}-{refmode}-{looplvl}-{loopshp}"
    ".webm".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{ipmode}-{qp}-{quality}-{refmode}-{looplvl}-{loopshp}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! videoconvert ! video/x-raw,format={hwup_format}"
    " ! vaapivp9enc rate-control=cqp keyframe-period={gop}"
    " yac-qi={qp} quality-level={quality} ref-pic-mode={refmode}"
    " loop-filter-level={looplvl} sharpness-level={loopshp} ! matroskamux"
    " ! filesink location={encoded}".format(**params))

  check_psnr(params)

#-------------------------------------------------#
#---------------------- CBR ----------------------#
#-------------------------------------------------#
@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapivp9enc"))
@slash.requires(*have_gst_element("vaapivp9dec"))
@slash.parametrize(*gen_vp9_cbr_parameters(spec))
@platform_tags(VP9_ENCODE_8BIT_PLATFORMS)
def test_8bit_cbr(case, gop, bitrate, fps, refmode, looplvl, loopshp):
  params = spec[case].copy()

  params.update(
    gop = gop, bitrate = bitrate, fps = fps, refmode = refmode,
    looplvl = looplvl, loopshp = loopshp, mformat = mapformat(params["format"]),
    frames = params.get("brframes", params["frames"]),
    hwup_format = mapformat_hwup(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{bitrate}-{fps}-{refmode}-{looplvl}-{loopshp}"
    ".webm".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{bitrate}-{fps}-{refmode}-{looplvl}-{loopshp}"
    "-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " framerate={fps} ! videoconvert ! video/x-raw,format={hwup_format}"
    " ! vaapivp9enc rate-control=cbr keyframe-period={gop} bitrate={bitrate}"
    " ref-pic-mode={refmode} loop-filter-level={looplvl}"
    " sharpness-level={loopshp} ! matroskamux"
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
@slash.requires(*have_gst_element("vaapivp9enc"))
@slash.requires(*have_gst_element("vaapivp9dec"))
@slash.parametrize(*gen_vp9_vbr_parameters(spec))
@platform_tags(VP9_ENCODE_8BIT_PLATFORMS)
def test_8bit_vbr(case, gop, bitrate, fps, refmode, quality, looplvl, loopshp):
  params = spec[case].copy()

  # target percentage 70% (hard-coded in gst-vaapi)
  # gst-vaapi sets max-bitrate = bitrate and min-bitrate = bitrate * 0.70
  minrate = bitrate
  maxrate = int(bitrate / 0.7)

  params.update(
    gop = gop, bitrate = bitrate, fps = fps, refmode = refmode,
    quality = quality, looplvl = looplvl, loopshp = loopshp, minrate = minrate,
    maxrate = maxrate, mformat = mapformat(params["format"]),
    frames = params.get("brframes", params["frames"]),
    hwup_format = mapformat_hwup(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{bitrate}-{fps}-{refmode}-{quality}-{looplvl}-{loopshp}"
    ".webm".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{bitrate}-{fps}-{refmode}-{quality}-{looplvl}-{loopshp}"
    "-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " framerate={fps} ! videoconvert ! video/x-raw,format={hwup_format}"
    " ! vaapivp9enc rate-control=vbr keyframe-period={gop} bitrate={maxrate}"
    " ref-pic-mode={refmode} loop-filter-level={looplvl}"
    " sharpness-level={loopshp} quality-level={quality} ! matroskamux"
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
