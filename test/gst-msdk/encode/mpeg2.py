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
    " ! mpegvideoparse ! msdkmpeg2dec hardware=true"
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
@slash.requires(have_gst_msdk)
@slash.requires(have_gst_msdkmpeg2enc)
@slash.requires(have_gst_msdkmpeg2dec)
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_mpeg2_cqp_parameters(spec, ['high', 'main', 'simple']))
@platform_tags(MPEG2_ENCODE_PLATFORMS)
def test_cqp(case, gop, bframes, qp, quality, profile):
  params = spec[case].copy()

  mprofile = mapprofile("mpeg2", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    gop = gop, bframes = bframes, qp = qp, mqp = mapRange(qp, [0, 100], [0, 51]),
    quality = quality, profile = mprofile, mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{bframes}-{qp}-{quality}-{profile}"
    ".mpg".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{bframes}-{qp}-{quality}-{profile}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! videoconvert ! video/x-raw,format=NV12"
    " ! msdkmpeg2enc rate-control=cqp qpi={mqp} qpp={mqp} qpb={mqp}"
    " gop-size={gop} b-frames={bframes} hardware=true"
    " ! video/mpeg,mpegversion=2,profile={profile}"
    " ! mpegvideoparse ! filesink location={encoded}".format(**params))

  check_psnr(params)

