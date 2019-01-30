###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

#-------------------------------------------------#
#----------------------8BIT-----------------------#
#-------------------------------------------------#

spec_8bit = load_test_spec("vp9", "decode", "8bit")

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(have_ffmpeg_vp9_qsv_decode)
@slash.requires(using_compatible_driver)
@slash.parametrize(("case"), sorted(spec_8bit.keys()))
@platform_tags(VP9_DECODE_8BIT_PLATFORMS)
def test_8bit(case):
  params = spec_8bit[case].copy()

  params.update(mformat = mapformat(params["format"]))
  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  params["decoded"] = get_media()._test_artifact(
    "{}_{width}x{height}_{format}.yuv".format(case, **params))

  output = call(
    "ffmpeg -hwaccel qsv -hwaccel_device /dev/dri/renderD128 -v verbose"
    " -c:v vp9_qsv -i {source} -vf 'hwdownload,format=nv12'"
    " -pix_fmt {mformat} -f rawvideo -vsync passthrough"
    " -vframes {frames} -y {decoded}".format(**params))

  m = re.search("No support for codec vp9", output, re.MULTILINE)
  assert m is None, "Failed to use hardware decode"

  m = re.search("Initialize MFX session", output, re.MULTILINE)
  assert m is not None, "It appears that the QSV plugin did not load"

  params.setdefault(
    "metric", dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0))
  check_metric(**params)

#-------------------------------------------------#
#---------------------10BIT-----------------------#
#-------------------------------------------------#

spec_10bit = load_test_spec("vp9", "decode", "10bit")

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(have_ffmpeg_vp9_qsv_decode)
@slash.requires(using_compatible_driver)
@platform_tags(VP9_DECODE_10BIT_PLATFORMS)
@slash.parametrize(("case"), sorted(spec_10bit.keys()))
def test_10bit(case):
  params = spec_10bit[case].copy()

  params.update(mformat = mapformat(params["format"]))
  if params["mformat"] is None:
    slash.skip_test("{format} format not supported".format(**params))

  params["decoded"] = get_media()._test_artifact(
    "{}_{width}x{height}_{format}.yuv".format(case, **params))

  output = call(
    "ffmpeg -hwaccel qsv -hwaccel_device /dev/dri/renderD128 -v verbose"
    " -c:v vp9_qsv -i {source} -vf 'hwdownload,format=p010le'"
    " -pix_fmt {mformat} -f rawvideo -vsync passthrough"
    " -vframes {frames} -y {decoded}".format(**params))

  m = re.search("No support for codec vp9", output, re.MULTILINE)
  assert m is None, "Failed to use hardware decode"

  m = re.search("Initialize MFX session", output, re.MULTILINE)
  assert m is not None, "It appears that the QSV plugin did not load"

  params.setdefault(
    "metric", dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0))
  check_metric(**params)
