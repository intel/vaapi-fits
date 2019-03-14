###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
import os

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
class TranscoderTest(slash.Test):
  def before(self):
    self.refctx = []

  def transcode_1to1(self):
    self.decoded = get_media()._test_artifact(
      "{case}_{width}x{height}_{mode}.{dstextension}".format(**vars(self)))

    if vars(self).get("dstextension", None) == 'mjpeg':
      self.mjpeg_quality = "-global_quality 60"
    else:
      self.mjpeg_quality = ""

    if vars(self).get("mode", None) == 'hwhw':
      self.output = call(
        "ffmpeg -hwaccel qsv -hwaccel_device /dev/dri/renderD128 -v verbose"
        " -c:v {ffdecoder} -i {source} -an -init_hw_device qsv:hw -c:v {ffencoder}"
        " -vframes {frames} -y {decoded}".format(**vars(self)))
    elif  vars(self).get("mode", None) == 'hwsw':
      self.output = call(
        "ffmpeg -v verbose -init_hw_device qsv:hw"
        "  -c:v {ffdecoder} -i {source}  -an -c:v {ffencoder}"
        " {mjpeg_quality} -vframes {frames} -y {decoded}".format(**vars(self)))
    elif  vars(self).get("mode", None) == 'swhw':
      self.output = call(
        "ffmpeg -hwaccel qsv -init_hw_device qsv=hw -filter_hw_device hw -v verbose "
        " -c:v {ffdecoder} -i {source} -an -vf hwupload=extra_hw_frames=64,format=qsv  -c:v {ffencoder}"
        " {mjpeg_quality} -vframes {frames} -y {decoded}".format(**vars(self)))
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
       "{case}_{width}x{height}_{mode}_{ffencoder}.yuv".format(**vars(self)))
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
