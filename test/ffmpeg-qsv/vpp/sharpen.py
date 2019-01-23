###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "sharpen")

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(*have_ffmpeg_filter("vpp_qsv"))
@slash.requires(using_compatible_driver)
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
    level = level, mformat = mapformat(params["format"]))
  params["ofile"] = get_media()._test_artifact(
    "{}_sharpen_{level}_{format}_{width}x{height}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  call(
    "ffmpeg -init_hw_device qsv=qsv:hw -hwaccel qsv -filter_hw_device qsv"
    " -v debug -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -i {source}"
    " -vf 'format=nv12,hwupload=extra_hw_frames=16"
    ",vpp_qsv=detail={level},hwdownload,format=nv12'"
    " -pix_fmt {mformat} -an -vframes {frames} -y {ofile}".format(**params))

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
