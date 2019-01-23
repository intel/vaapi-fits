###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

spec = load_test_spec("jpeg", "encode")

def check_output(output):
  m = re.search("Using VAAPI profile VAProfileJPEGBaseline ([0-9]*)", output, re.MULTILINE)
  assert m is not None, "Possible incorrect profile used"

  rcmsg = ("Using constant-quality mode|RC mode: CQP"
    "|Driver does not report any supported rate control modes:"
    " assuming constant-quality")

  m = re.search(rcmsg, output, re.MULTILINE)
  assert m is not None, "Possible incorrect RC mode used"

  m = re.search("Using intra frames only", output, re.MULTILINE)
  assert m is not None, "Possible incorrect IPB mode used"

  m = re.search("Using VAAPI entrypoint VAEntrypointEncPicture ([0-9]*)", output, re.MULTILINE)
  assert m is not None, "Possible incorrect entrypoint used"


@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(have_ffmpeg_mjpeg_vaapi_encode)
@slash.parametrize(*gen_jpeg_cqp_parameters(spec))
@platform_tags(JPEG_ENCODE_PLATFORMS)
def test_cqp(case, quality):
  params = spec[case].copy()
  params.update(
    quality = quality, ext = "mjpeg" if params["frames"] > 1 else "jpg",
    mformat = mapformat(params["format"]))
  params["encoded"] = get_media()._test_artifact(
    "{}-{quality}.{ext}".format(case, **params))
  params["decoded"] = get_media()._test_artifact(
    "{}-{quality}-{width}x{height}-{format}.yuv".format(case, **params))

  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  output = call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v debug"
    " -f rawvideo -pix_fmt {mformat} -s:v {width}x{height} -i {source}"
    " -vf 'format=nv12,hwupload' -c:v mjpeg_vaapi -global_quality {quality}"
    " -vframes {frames} -y {encoded}".format(**params))

  check_output(output)

  call(
    "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v debug"
    " -i {encoded} -pix_fmt {mformat} -f rawvideo -vsync passthrough"
    " -vframes {frames} -y {decoded}".format(**params))

  get_media().baseline.check_psnr(
    psnr = calculate_psnr(
      params["source"], params["decoded"],
      params["width"], params["height"],
      params["frames"], params["format"]),
    context = params.get("refctx", []),
  )
