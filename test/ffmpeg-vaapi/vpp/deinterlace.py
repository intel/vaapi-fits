###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("vpp", "deinterlace")
spec_r2r = load_test_spec("vpp", "deinterlace", "r2r")

def init(tspec, case, method):
  tparams = tspec[case].copy()
  tparams.update(
    method = map_deinterlace_method(method),
    mformat = mapformat(tparams["format"]),
    tff = tparams.get("tff", 1))

  if tparams["method"] is None:
    slash.skip_test("{} method not supported".format(method))

  if tparams["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**tparams))

  return tparams

def call_ffmpeg(params):
  call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v debug"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -top {tff}"
    " -i {source} -vf 'format=nv12,hwupload,deinterlace_vaapi=mode={method}"
    ":rate=field,hwdownload,format=nv12'"
    " -pix_fmt {mformat} -vframes {frames} -y {decoded}".format(**params))

def gen_output(case, params):
  name = "{case}_deinterlace_{method}_{format}_{width}x{height}".format(case = case, **params)

  if params.get("r2r", None) is not None:
    name += "_r2r"

  name += ".yuv"
  params["decoded"] =  get_media()._test_artifact(name)

  call_ffmpeg(params)

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(*have_ffmpeg_filter("deinterlace_vaapi"))
@slash.parametrize(*gen_vpp_deinterlace_parameters(spec, ["bob", "weave", "motion-adaptive", "motion-compensated"]))
@platform_tags(VPP_PLATFORMS)
def test_default(case, method):
  params = init(spec, case, method)

  gen_output(case, params)

  params.setdefault("metric", dict(type = "md5"))
  check_metric(**params)

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(*have_ffmpeg_filter("deinterlace_vaapi"))
@slash.parametrize(*gen_vpp_deinterlace_parameters(spec_r2r, ["bob", "weave", "motion-adaptive", "motion-compensated"]))
@platform_tags(VPP_PLATFORMS)
def test_r2r(case, method):
  params = init(spec_r2r, case, method)
  params.setdefault("r2r", 5)
  assert type(params["r2r"]) is int and params["r2r"] > 1, "invalid r2r value"

  gen_output(case, params)

  md5ref = md5(params["decoded"])
  get_media()._set_test_details(md5_ref = md5ref)

  for i in xrange(1, params["r2r"]):
    params["decoded"] = get_media()._test_artifact(
      "{case}_deinterlace_{method}_{format}_{width}x{height}_{i}"
      ".yuv".format(case = case, i = i, **params))

    call_ffmpeg(params)
    result = md5(params["decoded"])
    get_media()._set_test_details(**{ "md5_{:03}".format(i) : result})
    assert result == md5ref, "r2r md5 mismatch"
    #delete decoded file after each iteration
    get_media()._purge_test_artifact(params["decoded"])
