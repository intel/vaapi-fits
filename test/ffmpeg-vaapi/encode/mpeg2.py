###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("mpeg2", "encode")

def check_output(output, rcmode, gop, bframes, profile):

  ipbmode = 0 if gop <= 1 else 1 if bframes < 1 else 2

  ipbmsgs = [
    "Using intra frames only",
    "Using intra and P-frames",
    "Using intra, P- and B-frames"
  ]
  profilemsgs = {
    "simple"                :
      "Using VAAPI profile VAProfileMPEG2Simple ([0-9]*)",
    "main"                  :
      "Using VAAPI profile VAProfileMPEG2Main ([0-9]*)",
  }
  rcmsgs = dict(
    cqp = "Using constant-quality mode|RC mode: CQP",
    cbr = "RC mode: CBR",
    vbr = "RC mode: VBR",
  )

  m = re.search(profilemsgs[profile], output, re.MULTILINE)
  assert m is not None, "Possible incorrect profile used"

  m = re.search(rcmsgs[rcmode], output, re.MULTILINE)
  assert m is not None, "Possible incorrect RC mode used"

  m = re.search(ipbmsgs[ipbmode], output, re.MULTILINE)
  assert m is not None, "Possible incorrect IPB mode used"

def check_psnr(params):
  call(
    "ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -v verbose"
    " -i {encoded} -pix_fmt {mformat} -f rawvideo -vsync passthrough"
    " -vframes {frames} -y {decoded}".format(**params))

  get_media().baseline.check_psnr(
    psnr = calculate_psnr(
      params["source"], params["decoded"],
      params["width"], params["height"],
      params["frames"], params["format"]),
    context = params.get("refctx", []),
  )

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(have_ffmpeg_mpeg2_vaapi_encode)
@slash.parametrize(*gen_mpeg2_cqp_parameters(spec, ['main', 'simple']))
@platform_tags(MPEG2_ENCODE_PLATFORMS)
def test_cqp(case, gop, bframes, qp, quality, profile):
  params = spec[case].copy()

  mprofile = mapprofile("mpeg2", profile)
  if mprofile is None:
    slash.skip_test("{} profile is not supported".format(profile))

  params.update(
    gop = gop, bframes = bframes, qp = qp, quality = quality, profile = profile,
    mprofile = mprofile, mformat = mapformat(params["format"]))

  params["encoded"] = get_media()._test_artifact(
    "{}-{gop}-{bframes}-{qp}-{quality}-{profile}"
    ".m2v".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{gop}-{bframes}-{qp}-{quality}-{profile}-{width}x{height}-{format}"
    ".yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  slash.logger.notice("NOTICE: 'quality' parameter unused (not supported by plugin)")

  output = call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -i {source}"
    " -vf 'format=nv12,hwupload' -c:v mpeg2_vaapi -profile:v {mprofile}"
    " -g {gop} -bf {bframes} -global_quality {qp}"
    " -vframes {frames} -y {encoded}".format(**params))

  check_output(output, "cqp", gop, bframes, profile)

  check_psnr(params)
