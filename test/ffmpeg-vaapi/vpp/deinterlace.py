###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "deinterlace")

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(*have_ffmpeg_filter("deinterlace_vaapi"))
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

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v debug"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -top {tff}"
    " -i {source} -vf 'format=nv12,hwupload,deinterlace_vaapi=mode={method}"
    ":rate=field,hwdownload,format=nv12'"
    " -pix_fmt {mformat} -vframes {frames} -y {decoded}".format(**params))

  params.setdefault("metric", dict(type = "md5"))
  check_metric(**params)
