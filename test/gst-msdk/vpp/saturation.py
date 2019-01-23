###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "saturation")

NOOP = 10 # i.e. 1.0 in msdkvpp range should result in no-op result

@slash.requires(have_gst)
@slash.requires(*have_gst_element("msdk"))
@slash.requires(*have_gst_element("msdkvpp"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_vpp_saturation_parameters(spec))
@platform_tags(VPP_PLATFORMS)
def test_default(case, level):
  params = spec[case].copy()
  params.update(
    level = level, mlevel = mapRange(level, [0, 100], [0.0, 10.0]),
    mformat = mapformat(params["format"]))
  params["ofile"] = get_media()._test_artifact(
    "{}_saturation_{level}_{format}_{width}x{height}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! msdkvpp hardware=true saturation={mlevel} ! video/x-raw,format=NV12"
    " ! videoconvert ! video/x-raw,format={format}"
    " ! checksumsink2 file-checksum=false frame-checksum=false"
    " plane-checksum=false dump-output=true dump-location={ofile}"
    "".format(**params))

  psnr = calculate_psnr(
    params["source"], params["ofile"],
    params["width"], params["height"],
    params["frames"], params["format"])

  def compare(k, ref, actual):
    assert psnr[-3] == 100, "Luma (Y) should not be affected by SATURATION filter"
    if params["level"] == NOOP:
      assert psnr[-2] == 100, "Cb (U) should not be affected at NOOP level"
      assert psnr[-1] == 100, "Cr (V) should not be affected at NOOP level"
    else:
      assert ref is not None, "Invalid reference value"
      assert abs(ref[-2] - actual[-2]) <  0.2, "Cb (U) out of baseline range"
      assert abs(ref[-1] - actual[-1]) <  0.2, "Cr (V) out of baseline range"

  get_media().baseline.check_result(
    compare = compare, context = params.get("refctx", []), psnr = psnr)
