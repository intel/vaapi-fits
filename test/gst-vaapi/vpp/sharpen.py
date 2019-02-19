###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "sharpen")

@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("vaapipostproc"))
@slash.requires(*have_gst_element("checksumsink2"))
@slash.parametrize(*gen_vpp_sharpen_parameters(spec))
@platform_tags(VPP_PLATFORMS)
def test_default(case, level):
  params = spec[case].copy()

  if params["width"] == 1280 and params["height"] == 720:
    if os.environ.get("LIBVA_DRIVER_NAME", "i965") == "i965":
      slash.add_failure(
        "1280x720 resolution is known to cause GPU HANG with i965 driver")
      return

  params.update(
    level = level, mlevel = mapRange(level, [0, 100], [-1.0, 1.0]),
    mformat = mapformat(params["format"]),
    hwup_format = mapformat_hwup(params["format"]))
  params["ofile"] = get_media()._test_artifact(
    "{}_sharpen_{level}_{format}_{width}x{height}"
    ".yuv".format(case, **params))

  call(
    "gst-launch-1.0 -vf filesrc location={source} num-buffers={frames}"
    " ! rawvideoparse format={mformat} width={width} height={height}"
    " ! videoconvert ! video/x-raw, format={hwup_format}"
    " ! vaapipostproc format={mformat} width={width} height={height}"
    " sharpen={mlevel} ! checksumsink2 file-checksum=false"
    " frame-checksum=false plane-checksum=false dump-output=true"
    " dump-location={ofile}".format(**params))

  psnr = calculate_psnr(
    params["source"], params["ofile"],
    params["width"], params["height"],
    params["frames"], params["format"])

  assert psnr[-2] == 100, "Cb(U) should not be affected by SHARPEN filter"
  assert psnr[-1] == 100, "Cr(V) should not be affected by SHARPEN filter"

  def compare(k, ref, actual):
    assert ref is not None, "Invalid reference value"
    assert abs(ref[-3] - actual[-3]) <  0.2, "Luma (Y) out of baseline range"

  get_media().baseline.check_result(
    compare = compare, context = params.get("refctx", []), psnr = psnr)
