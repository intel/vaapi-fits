###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vp8", "decode")

@slash.requires(have_gst)
@slash.requires(have_gst_msdk)
@slash.requires(have_gst_msdkvp8dec)
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(("case"), sorted(spec.keys()))
@platform_tags(VP8_DECODE_PLATFORMS)
def test_default(case):
  params = spec[case].copy()

  params.update(mformatu = mapformatu(params["format"]))

  if params["mformatu"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  params["decoded"] = get_media()._test_artifact(
    "{}_{width}x{height}_{format}.yuv".format(case, **params))

  dxmap = {".ivf" : "ivfparse", ".webm" : "matroskademux"}
  ext = os.path.splitext(params["source"])[1]
  assert ext in dxmap.keys(), "Unrecognized source file extension {}".format(ext)
  params["demux"] = dxmap[ext]

  call(
    "gst-launch-1.0 -vf filesrc location={source}"
    " ! {demux} ! msdkvp8dec"
    " ! videoconvert ! video/x-raw,format={mformatu}"
    " ! checksumsink2 file-checksum=false frame-checksum=false"
    " plane-checksum=false dump-output=true qos=false"
    " dump-location={decoded}".format(**params))

  params.setdefault(
    "metric", dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0))
  check_metric(**params)
