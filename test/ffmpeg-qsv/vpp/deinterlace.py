###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "deinterlace")

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(*have_ffmpeg_filter("vpp_qsv"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_vpp_deinterlace_parameters(spec, ["bob", "advanced"]))
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


  # TODO: how to configure vpp_qsv to use field rate?
  call(
    "ffmpeg -init_hw_device qsv=qsv:hw -hwaccel qsv -filter_hw_device qsv"
    " -v debug -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -top {tff}"
    " -i {source} -vf 'format=nv12,hwupload=extra_hw_frames=16"
    ",vpp_qsv=deinterlace={method},hwdownload,format=nv12'"
    " -pix_fmt {mformat} -an -vframes {frames} -y {decoded}".format(**params))

  params.setdefault("metric", dict(type = "md5"))
  check_metric(**params)
