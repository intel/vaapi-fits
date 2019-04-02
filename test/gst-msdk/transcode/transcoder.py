###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
import os

@slash.requires(have_gst)
@slash.requires(*have_gst_element("msdk"))
@slash.requires(*have_gst_element("checksumsink2"))
class TranscoderTest(slash.Test):
  def before(self):
    self.refctx = []

  def transcode_1to1(self):
    self.transcoded = get_media()._test_artifact(
      "{case}_{width}x{height}_{mode}.{dstextension}".format(**vars(self)))
    call("gst-launch-1.0 -vf filesrc location={source} ! {gsttrans}"
      " ! filesink location={transcoded}".format(**vars(self)))

    self.convert_toyuv()
    self.check_metrics()

  def convert_toyuv(self):
    self.decodedYUV = get_media()._test_artifact(
       "{case}_{width}x{height}_{mode}_{trans_type}.yuv".format(**vars(self)))
    call("gst-launch-1.0 -vf filesrc location={transcoded}"
      " ! {gstdecoder2}"
      " ! videoconvert ! video/x-raw,format=I420"
      " ! checksumsink2 file-checksum=false qos=false"
      " frame-checksum=false plane-checksum=false dump-output=true"
      " dump-location={decodedYUV}".format(**vars(self)))

    #src file to yuv
    self.referenceFile = get_media()._test_artifact(
       "{case}_{width}x{height}_{mode}_ref.yuv".format(**vars(self)))
    call("gst-launch-1.0 -vf filesrc location={source}"
      " ! {gstdecoder1}"
      " ! videoconvert ! video/x-raw,format=I420"
      " ! checksumsink2 file-checksum=false qos=false"
      " frame-checksum=false plane-checksum=false dump-output=true"
      " dump-location={referenceFile}".format(**vars(self)))

  def check_metrics(self):
    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.referenceFile, self.decodedYUV,
        self.width, self.height,
        self.frames),
      context = self.refctx,
    )
