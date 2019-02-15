###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
import os

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
class TranscoderTest(slash.Test):
  def before(self):
    self.refctx = []

  def transcode_1to1(self):
    self.decoded = get_media()._test_artifact(
      "{case}_{width}x{height}_{mode}.{dstextension}".format(**vars(self)))
    if vars(self).get("mode", None) == 'hwhw':
      self.output = call(
        "ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -v verbose"
        "  -hwaccel_output_format vaapi -i {source} -an -c:v {mcodec}"
        " -vframes {frames} -y {decoded}".format(**vars(self)))
    elif  vars(self).get("mode", None) == 'hwsw':
      self.output = call(
        "ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -v verbose"
        "  -hwaccel_output_format vaapi -i {source}  -vf 'hwdownload,format=nv12' -an -c:v {mcodec}"
        " -vframes {frames} -y {decoded}".format(**vars(self)))
    elif  vars(self).get("mode", None) == 'swhw':
      self.output = call(
        "ffmpeg -vaapi_device /dev/dri/renderD128 -v verbose "
        "-i {source}  -vf 'hwupload,format=nv12' -an -c:v {mcodec}"
        " -vframes {frames} -y {decoded}".format(**vars(self)))
    else:
        assert "non supported transcoding"

    self.check_output()
    self.convert_toyuv()
    self.check_metrics()

  def check_output(self):
    m = re.search(
      "not supported for hardware decode", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"

    m = re.search(
      "hwaccel initialisation returned error", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"
  
  def convert_toyuv(self):
    self.decodedYUV = get_media()._test_artifact(
       "{case}_{width}x{height}_{mode}_{mcodec}.yuv".format(**vars(self)))
    call("ffmpeg -i {decoded} -pix_fmt yuv420p -vframes {frames} -y {decodedYUV}".format(**vars(self)))

    #src file to yuv
    self.referenceFile = get_media()._test_artifact(
       "{case}_{width}x{height}_{mode}_ref.yuv".format(**vars(self)))
    call("ffmpeg -i {source} -pix_fmt yuv420p -vframes {frames} -y {referenceFile}".format(**vars(self)))

  def check_metrics(self):
    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.referenceFile, self.decodedYUV,
        self.width, self.height,
        self.frames),
      context = self.refctx,
    )
