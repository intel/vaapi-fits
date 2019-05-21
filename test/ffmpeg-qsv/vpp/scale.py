###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "scale")
spec_r2r = load_test_spec("vpp", "scale", "r2r")

def init(tspec, case, scale_width, scale_height):
  tparams = tspec[case].copy()
  tparams.update(
    mformat = mapformat(tparams["format"]),
    scale_width = scale_width, scale_height = scale_height)

  if tparams["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**tparams))

  return tparams

def call_ffmpeg(params):
  call(
    "ffmpeg -init_hw_device qsv=qsv:hw -hwaccel qsv -filter_hw_device qsv"
    " -v debug -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -i {source}"
    " -vf 'format=nv12,hwupload=extra_hw_frames=16"
    ",vpp_qsv=w={scale_width}:h={scale_height},hwdownload,format=nv12'"
    " -pix_fmt {mformat} -an -vframes {frames} -y {scaled}".format(**params))

def gen_output(case, params):
  name = "{case}_scaled_{scale_width}x{scale_height}_{format}".format(case = case, **params)

  if params.get("r2r", None) is not None:
    name += "_r2r"

  name += ".yuv"
  params["scaled"] = get_media()._test_artifact(name)

  call_ffmpeg(params)

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(*have_ffmpeg_filter("vpp_qsv"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_vpp_scale_parameters(spec))
@platform_tags(VPP_PLATFORMS)
def test_default(case, scale_width, scale_height):
  params = init(spec, case, scale_width, scale_height)

  gen_output(case, params)

  check_filesize(
    params["scaled"], params["scale_width"], params["scale_height"],
    params["frames"], params["format"])

  fmtref = format_value(params["reference"], case = case, **params)

  ssim = calculate_ssim(
    fmtref, params["scaled"],
    params["scale_width"], params["scale_height"],
    params["frames"], params["format"])

  get_media()._set_test_details(ssim = ssim)

  assert 1.0 >= ssim[0] >= 0.97
  assert 1.0 >= ssim[1] >= 0.97
  assert 1.0 >= ssim[2] >= 0.97

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(*have_ffmpeg_filter("vpp_qsv"))
@slash.requires(using_compatible_driver)
@slash.parametrize(*gen_vpp_scale_parameters(spec_r2r))
@platform_tags(VPP_PLATFORMS)
def test_r2r(case, scale_width, scale_height):
  params = init(spec_r2r, case, scale_width, scale_height)
  params.setdefault("r2r", 5)
  assert type(params["r2r"]) is int and params["r2r"] > 1, "invalid r2r value"

  gen_output(case, params)

  md5ref = md5(params["scaled"])
  get_media()._set_test_details(md5_ref = md5ref)

  for i in xrange(1, params["r2r"]):
    params["scaled"] = get_media()._test_artifact(
      "{case}_scaled_{scale_width}x{scale_height}_{format}_{i}"
      ".yuv".format(case = case, i = i, **params))

    call_ffmpeg(params)
    result = md5(params["scaled"])
    get_media()._set_test_details(**{ "md5_{:03}".format(i) : result})
    assert result == md5ref, "r2r md5 mismatch"
    #delete scaled file after each iteration
    get_media()._purge_test_artifact(params["scaled"])
