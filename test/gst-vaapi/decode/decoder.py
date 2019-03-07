###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

@slash.requires(have_gst)
@slash.requires(*have_gst_element("vaapi"))
@slash.requires(*have_gst_element("checksumsink2"))
class DecoderTest(slash.Test):
  def before(self):
    self.refctx = []

  def decode(self):
    self.mformatu = mapformatu(self.format)
    if self.mformatu is None:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    self.decoded = get_media()._test_artifact(
      "{case}_{width}x{height}_{format}.yuv".format(**vars(self)))

    call(
      "gst-launch-1.0 -vf filesrc location={source}"
      " ! {gstdecoder}"
      " ! videoconvert ! video/x-raw,format={mformatu}"
      " ! checksumsink2 file-checksum=false qos=false"
      " frame-checksum=false plane-checksum=false dump-output=true"
      " dump-location={decoded}".format(**vars(self)))

    self.check_metrics()

  def check_metrics(self):
    check_metric(**vars(self))
