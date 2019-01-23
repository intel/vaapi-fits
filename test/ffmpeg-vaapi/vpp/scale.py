###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "scale")

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(*have_ffmpeg_filter("scale_vaapi"))
@slash.parametrize(*gen_vpp_scale_parameters(spec))
@platform_tags(VPP_PLATFORMS)
def test_default(case, scale_width, scale_height):
  params = spec[case].copy()
  params.update(
    mformat = mapformat(params["format"]),
    scale_width = scale_width, scale_height = scale_height)

  params["scaled"] = get_media()._test_artifact(
    "{}_scaled_{scale_width}x{scale_height}_{format}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v debug"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -i {source}"
    " -vf 'format=nv12,hwupload,scale_vaapi=w={scale_width}:h={scale_height}"
    ",hwdownload,format=nv12'"
    " -pix_fmt {mformat} -vframes {frames} -y {scaled}".format(**params))

  check_filesize(
    params["scaled"], params["scale_width"], params["scale_height"],
    params["frames"], params["format"])

  fmtref = format_value(params["reference"], case = case, **params)

  ssim = calculate_ssim(
    fmtref, params["scaled"],
    params["scale_width"], params["scale_height"],
    params["frames"], params["format"])

  get_media()._set_test_details(ssim = ssim)

  assert 1.0 >= ssim[0] >= 0.97
  assert 1.0 >= ssim[1] >= 0.97
  assert 1.0 >= ssim[2] >= 0.97
