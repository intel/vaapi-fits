###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "scale")

@slash.requires(have_gst)
@slash.requires(*have_gst_element("msdk"))
@slash.requires(*have_gst_element("msdkvpp"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
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

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! msdkvpp hardware=true scaling-mode=1 ! video/x-raw,format=NV12"
    " ! videoconvert"
    " ! video/x-raw,width={scale_width},height={scale_height},format={format}"
    " ! checksumsink2 file-checksum=false frame-checksum=false"
    " plane-checksum=false dump-output=true dump-location={scaled}"
    "".format(**params))

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
