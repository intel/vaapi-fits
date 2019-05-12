###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "transpose")

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(*have_ffmpeg_filter("transpose_vaapi"))
@slash.parametrize(*gen_vpp_transpose_parameters(spec))
@platform_tags(VPP_PLATFORMS)
def test_default(case, degrees, method):
  params = spec[case].copy()
  params.update(
    degrees = degrees, method = method,
    direction = map_transpose_direction(degrees, method),
    mformat = mapformat(params["format"]))

  if params["direction"] is None:
    slash.skip_test("{} {} direction not supported".format(degrees, method))

  params["decoded"] = get_media()._test_artifact(
    "{}_rotation_{degrees}_{method}_{format}_{width}x{height}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v debug"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -i {source}"
    " -vf 'format=nv12,hwupload,transpose_vaapi=dir={direction}"
    ",hwdownload,format=nv12'"
    " -pix_fmt {mformat} -vframes {frames} -y {decoded}".format(**params))

  params.setdefault("metric", dict(type = "md5"))
  check_metric(**params)
