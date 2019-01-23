###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vc1", "decode")

@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapivc1dec"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(("case"), sorted(spec.keys()))
@platform_tags(VC1_DECODE_PLATFORMS)
def test_default(case):
  params = spec[case].copy()

  params.update(mformatu = mapformatu(params["format"]))

  if params["mformatu"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  params["decoded"] = get_media()._test_artifact(
    "{}_{width}x{height}_{format}.yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source}"
    " ! 'video/x-wmv,profile=(string)advanced'"
    " ,width={width},height={height},framerate=14/1"
    " ! vaapivc1dec"
    " ! videoconvert ! video/x-raw,format={mformatu}"
    " ! checksumsink2 file-checksum=false qos=false"
    " frame-checksum=false plane-checksum=false dump-output=true"
    " dump-location={decoded}".format(**params))

  params.setdefault(
    "metric", dict(type = "ssim", miny = 0.99, minu = 0.99, minv = 0.99))
  check_metric(**params)
