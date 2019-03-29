###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "csc")

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(*have_ffmpeg_filter("vpp_qsv"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_vpp_csc_parameters(spec))
@platform_tags(VPP_PLATFORMS)
def test_default(case, csc):
  params = spec[case].copy()
  params.update(
    csc = csc,mcsc = mapformat(csc),mformat = mapformat(params["format"]))

  params["ofile"] = get_media()._test_artifact(
    "{}_{format}_csc_{csc}_{width}x{height}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  if params["mcsc"] is None or params["mcsc"] == "yuv420p":
    slash.skip_test("{} format not supported".format(csc))

  call(
    "ffmpeg -init_hw_device qsv=hw -hwaccel qsv -filter_hw_device hw"
    " -v debug -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -i {source}"
    " -vf 'format=nv12,hwupload=extra_hw_frames=64"
    ",scale_qsv=format={mcsc},hwdownload,format={mcsc}'"
    " -f rawvideo -vsync passthrough -vframes {frames}"
    " -y {ofile}".format(**params))

  check_metric(
    # if user specified metric, then use it.  Otherwise, use ssim metric with perfect score
    metric = params.get("metric", dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)),
    # If user specified reference, use it.  Otherwise, assume source is the reference.
    reference = format_value(params["reference"], case = case, **params)
      if params.get("reference") else params["source"],
    decoded = params["ofile"],
    # if user specified reference, then assume it's format is the same as csc output format.
    # Otherwise, the format is the source format
    format = params["format"] if params.get("reference", None) is None else params["csc"],
    format2 = params["csc"],
    width = params["width"], height = params["height"], frames = params["frames"],
  )
