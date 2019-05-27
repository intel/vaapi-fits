###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "csc")

@slash.requires(have_gst)
@slash.requires(*have_gst_element("msdk"))
@slash.requires(*have_gst_element("msdkvpp"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_vpp_csc_parameters(spec))
@platform_tags(VPP_PLATFORMS)
def test_default(case, csc):
  params = spec[case].copy()
  params.update(
    csc = csc, mcscu = mapformatu(csc),
    mformat = mapformat(params["format"]))
  params["ofile"] = get_media()._test_artifact(
    "{}_{format}_csc_{csc}_{width}x{height}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! msdkvpp hardware=true ! video/x-raw,format={mcscu}"
    " ! checksumsink2 file-checksum=false frame-checksum=false"
    " plane-checksum=false dump-output=true dump-location={ofile}"
    "".format(**params))

  check_metric(
    # if user specified metric, then use it.  Otherwise, use ssim metric with perfect score
    metric = params.get("metric", dict(type = "ssim", miny = 0.99, minu = 0.99, minv = 0.99)
      if params.get("reference") else dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)),
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
