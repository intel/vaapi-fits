###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "deinterlace")

@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapipostproc"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_vpp_deinterlace_parameters(spec, ["bob", "weave", "motion-adaptive", "motion-compensated"]))
@platform_tags(VPP_PLATFORMS)
def test_default(case, method):
  params = spec[case].copy()
  params.update(
    method = map_deinterlace_method(method),
    mformat = mapformat(params["format"]),
    tff = params.get("tff", 1))

  if params["method"] is None:
    slash.skip_test("{} method not supported".format(method))

  params["decoded"] = get_media()._test_artifact(
    "{}_deinterlace_{method}_{format}_{width}x{height}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " interlaced=true top-field-first={tff}"
    " ! vaapipostproc format={mformat} width={width} height={height}"
    " deinterlace-mode=1 deinterlace-method={method} ! checksumsink2"
    " file-checksum=false frame-checksum=false plane-checksum=false"
    " dump-output=true dump-location={decoded}".format(**params))

  params.setdefault("metric", dict(type = "md5"))
  check_metric(**params)
