###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vp8", "encode")

def check_psnr(params):
  call(
    "gst-launch-1.0 -vf filesrc location={encoded}"
    " ! matroskademux ! msdkvp8dec hardware=true"
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
@slash.requires(have_gst_msdkvp8enc)
@slash.requires(have_gst_msdkvp8dec)
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_vp8_cqp_parameters(spec))
@platform_tags(VP8_ENCODE_PLATFORMS)
def test_cqp(case, ipmode, qp, quality, looplvl, loopshp):
  if looplvl != 0 or loopshp != 0:
    # will looplvl or loopshp be supported later?
    slash.skip_test("looplvl != 0 or loopshp != 0 not supported")

  params = spec[case].copy()
  params.update(
    ipmode = ipmode, qp = qp, quality = quality, looplvl = looplvl,
    loopshp = loopshp, gop = 30 if ipmode != 0 else 1,
    mformat = mapformat(params["format"]))
  params["encoded"] = get_media()._test_artifact(
    "{}-{ipmode}-{qp}-{quality}-{looplvl}-{loopshp}"
    ".webm".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "-{}-{ipmode}-{qp}-{quality}-{looplvl}-{loopshp}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! videoconvert ! video/x-raw,format=NV12"
    " ! msdkvp8enc rate-control=cqp qpp={qp} gop-size={gop} hardware=true"
    " target-usage={quality}"
    " ! matroskamux ! filesink location={encoded}".format(**params))

  check_psnr(params)

