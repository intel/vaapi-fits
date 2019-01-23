###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "denoise")

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(*have_ffmpeg_filter("denoise_vaapi"))
@slash.parametrize(*gen_vpp_denoise_parameters(spec))
@platform_tags(VPP_PLATFORMS)
def test_default(case, level):
  params = spec[case].copy()
  params.update(
    level = level, mlevel = mapRange(level, [0, 100], [0, 64]),
    mformat = mapformat(params["format"]))
  params["ofile"] = get_media()._test_artifact(
    "{}_denoise_{level}_{format}_{width}x{height}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v debug"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -i {source}"
    " -vf 'format=nv12,hwupload,denoise_vaapi=denoise={mlevel}"
    ",hwdownload,format=nv12'"
    " -pix_fmt {mformat} -vframes {frames} -y {ofile}".format(**params))

  psnr = calculate_psnr(
    params["source"], params["ofile"],
    params["width"], params["height"],
    params["frames"], params["format"])

  def compare(k, ref, actual):
    assert ref is not None, "Invalid reference value"
    assert abs(ref[-3] - actual[-3]) < 0.2, "Luma (Y) out of baseline range"
    assert abs(ref[-2] - actual[-2]) < 0.2, "Cb (U) out of baseline range"
    assert abs(ref[-1] - actual[-1]) < 0.2, "Cr (V) out of baseline range"

  get_media().baseline.check_result(
    compare = compare, context = params.get("refctx", []), psnr = psnr)
