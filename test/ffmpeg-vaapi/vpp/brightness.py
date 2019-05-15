###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "brightness")
spec_r2r = load_test_spec("vpp", "brightness", "r2r")

_NOOP_LEVEL = 50 # i.e. 0.0 in ffmpeg range

def init(tspec, case, level):
  tparams = tspec[case].copy()
  tparams.update(
    level = level, mlevel = mapRange(level, [0, 100], [-100.0, 100.0]),
    mformat = mapformat(tparams["format"]))

  if tparams["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**tparams))

  return tparams

def call_ffmpeg(params):
  call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v debug"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -i {source}"
    " -vf 'format=nv12,hwupload,procamp_vaapi=b={mlevel}"
    ",hwdownload,format=nv12'"
    " -pix_fmt {mformat} -vframes {frames} -y {ofile}".format(**params))

def gen_output(case, params):
  name = "{case}_brightness_{level}_{format}_{width}x{height}".format(case = case, **params)

  if params.get("r2r", None) is not None:
    name += "_r2r"

  name += ".yuv"
  params["ofile"] = get_media()._test_artifact(name)

  call_ffmpeg(params)

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(*have_ffmpeg_filter("procamp_vaapi"))
@slash.parametrize(*gen_vpp_brightness_parameters(spec))
@platform_tags(VPP_PLATFORMS)
def test_default(case, level):
  params = init(spec, case, level)

  gen_output(case, params)

  psnr = calculate_psnr(
    params["source"], params["ofile"],
    params["width"], params["height"],
    params["frames"], params["format"])

  assert psnr[-2] == 100, "Cb(U) should not be affected by BRIGHTNESS filter"
  assert psnr[-1] == 100, "Cr(V) should not be affected by BRIGHTNESS filter"

  if params["level"] == _NOOP_LEVEL:
    get_media()._set_test_details(psnr = psnr, ref_psnr = "noop")
    assert psnr[-3] == 100, "Luma (Y) should not be affected at NOOP level"
  else:
    def compare(k, ref, actual):
      assert ref is not None, "Invalid reference value"
      assert abs(ref[-3] - actual[-3]) <  0.2, "Luma (Y) out of baseline range"
    get_media().baseline.check_result(
      compare = compare, context = params.get("refctx", []), psnr = psnr)

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(*have_ffmpeg_filter("procamp_vaapi"))
@slash.parametrize(*gen_vpp_brightness_parameters(spec_r2r))
@platform_tags(VPP_PLATFORMS)
def test_r2r(case, level):
  params = init(spec_r2r, case, level)
  params.setdefault("r2r", 5)
  assert type(params["r2r"]) is int and params["r2r"] > 1, "invalid r2r value"

  gen_output(case, params)

  md5ref = md5(params["ofile"])
  get_media()._set_test_details(md5_ref = md5ref)

  for i in xrange(1, params["r2r"]):
    params["ofile"] = get_media()._test_artifact(
      "{case}_brightness_{level}_{format}_{width}x{height}_{i}"
      ".yuv".format(case = case, i = i, **params))

    call_ffmpeg(params)
    result = md5(params["ofile"])
    get_media()._set_test_details(**{ "md5_{:03}".format(i) : result})
    assert result == md5ref, "r2r md5 mismatch"
    #delete output file after each iteration
    get_media()._purge_test_artifact(params["ofile"])
