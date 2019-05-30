###
### Copyright (C) 2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "mirroring")

@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapipostproc"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_vpp_mirroring_parameters(spec))
@platform_tags(VPP_TRANSFORM_PLATFORMS)
def test_default(case, method):
  params = spec[case].copy()
  params.update(
    method = method, mmethod = map_vpp_mirroring(method),
    mformat = mapformat(params["format"]),
    hwup_format = mapformat_hwup(params["format"]))
  params["ofile"] = get_media()._test_artifact(
    "{case}_mirroring_{method}_{format}_{width}x{height}"
    ".yuv".format(case = case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! videoconvert ! video/x-raw, format={hwup_format}"
    " ! vaapipostproc format={mformat} width={width} height={height}"
    " video-direction={mmethod} ! checksumsink2 file-checksum=false"
    " frame-checksum=false plane-checksum=false dump-output=true"
    " dump-location={ofile}".format(**params))

  get_media().baseline.check_md5(
    md5 = md5(params["ofile"]), context = params.get("refctx", []))
