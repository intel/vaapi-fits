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
    "gst-launch-1.0 -vf filesrc location={encoded}"
    " ! mpegvideoparse ! vaapimpeg2dec"
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
@slash.requires(*have_gst_element("vaapimpeg2enc"))
@slash.requires(*have_gst_element("vaapimpeg2dec"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_mpeg2_cqp_parameters(spec, ['default']))
@platform_tags(MPEG2_ENCODE_PLATFORMS)
def test_cqp(case, gop, bframes, qp, quality, **unused):
  params = spec[case].copy()
  params.update(
    gop = gop, bframes = bframes, qp = qp, quality = quality,
    mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{bframes}-{qp}-{quality}"
    ".mpg".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{bframes}-{qp}-{quality}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! videoconvert ! video/x-raw,format=NV12"
    " ! vaapimpeg2enc rate-control=cqp quantizer={qp} keyframe-period={gop}"
    " max-bframes={bframes} quality-level={quality}"
    " ! mpegvideoparse ! filesink location={encoded}".format(**params))

  check_psnr(params)

