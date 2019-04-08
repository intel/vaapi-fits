###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "transpose")

@slash.requires(have_gst)
@slash.requires(*have_gst_element("msdk"))
@slash.requires(*have_gst_element("msdkvpp"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_vpp_transpose_parameters(spec))
@platform_tags(VPP_PLATFORMS)
def test_default(case, degrees, method):
  params = spec[case].copy()
  params.update(
    degrees = degrees, method = method, mmethod = map_vpp_mirroring(method),
    mformat = mapformat(params["format"]))
  params["ofile"] = get_media()._test_artifact(
    "{}_rotation_{degrees}_{method}_{format}_{width}x{height}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! msdkvpp hardware=true rotation={degrees} mirroring={mmethod}"
    " ! video/x-raw,format=NV12 ! videoconvert ! video/x-raw,format={format}"
    " ! checksumsink2 file-checksum=false frame-checksum=false"
    " plane-checksum=false dump-output=true dump-location={ofile}"
    "".format(**params))

  get_media().baseline.check_md5(
    md5 = md5(params["ofile"]), context = params.get("refctx", []))
