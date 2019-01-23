###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("jpeg", "encode")

@slash.requires(have_gst)
@slash.requires(have_gst_msdk)
@slash.requires(have_gst_msdkmjpegenc)
@slash.requires(have_gst_msdkmjpegdec)
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_jpeg_cqp_parameters(spec))
@platform_tags(JPEG_ENCODE_PLATFORMS)
def test_cqp(case, quality):
  params = spec[case].copy()
  params.update(quality = quality, mformat = mapformat(params["format"]),
    mformatu = mapformatu(params["format"]))
  params["encoded"] = get_media()._test_artifact(
    "{}-{quality}.jpg".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{quality}-{width}x{height}-{format}.yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! videoconvert ! video/x-raw,format=NV12"
    " ! msdkmjpegenc quality={quality} ! jpegparse"
    " ! filesink location={encoded}".format(**params))

  call(
    "gst-launch-1.0 -vf filesrc location={encoded}"
    " ! jpegparse ! msdkmjpegdec hardware=true"
    " ! videoconvert ! video/x-raw,format={mformatu}"
    " ! checksumsink2 file-checksum=false frame-checksum=false"
    " plane-checksum=false dump-output=true qos=false"
    " dump-location={decoded}".format(**params))

  get_media().baseline.check_psnr(
    psnr = calculate_psnr(
      params["source"], params["decoded"],
      params["width"], params["height"],
      params["frames"], params["format"]),
    context = params.get("refctx", []),
  )
