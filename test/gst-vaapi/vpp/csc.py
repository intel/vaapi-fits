###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "csc")

@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapipostproc"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_vpp_csc_parameters(spec))
@platform_tags(VPP_PLATFORMS)
def test_default(case, csc):
  params = spec[case].copy()
  params.update(
    csc = csc, mcsc = mapformat(csc), mformat = mapformat(params["format"]))
  params["ofile"] = get_media()._test_artifact(
    "{}_{format}_csc_{csc}_{width}x{height}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! vaapipostproc format={mcsc} ! checksumsink2 file-checksum=false"
    " frame-checksum=false plane-checksum=false dump-output=true"
    " dump-location={ofile}".format(**params))

  ssim = calculate_ssim(
    params["source"], params["ofile"],
    params["width"], params["height"], params["frames"],
    params["format"], params["csc"])

  get_media()._set_test_details(ssim = ssim)

  assert sum(ssim) == 6.0, "Y, U and V values should not be changed by CSC"
