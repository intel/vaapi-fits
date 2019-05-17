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

  def call_gst(self):
    self.gstscaler = ""
    if vars(self).get("scale_output", False):
      self.gstscaler = (
        " ! videoscale"
        " ! video/x-raw,width={width},height={height}".format(**vars(self)))

    call(
      "gst-launch-1.0 -vf filesrc location={source}"
      " ! {gstdecoder}"
      " ! videoconvert ! video/x-raw,format={mformatu} {gstscaler}"
      " ! checksumsink2 file-checksum=false qos=false"
      " frame-checksum=false plane-checksum=false dump-output=true"
      " dump-location={decoded}".format(**vars(self)))

  def gen_name(self):
    name = "{case}_{width}x{height}_{format}"
    if vars(self).get("r2r", None) is not None:
      name += "_r2r"
    return name

  def decode(self):
    self.mformatu = mapformatu(self.format)
    if self.mformatu is None:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    name = self.gen_name().format(**vars(self))
    self.decoded = get_media()._test_artifact("{}.yuv".format(name))
    self.call_gst()

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = md5(self.decoded)
      get_media()._set_test_details(md5_ref = md5ref)
      for i in xrange(1, self.r2r):
        self.decoded = get_media()._test_artifact(
          "{}_{}.yuv".format(name, i))
        self.call_gst()
        result = md5(self.decoded)
        get_media()._set_test_details(**{"md5_{:03}".format(i): result})
        assert result == md5ref, "r2r md5 mismatch"
        # delete decoded file after each iteration
        get_media()._purge_test_artifact(self.decoded)
    else:
      self.check_metrics()

  def check_metrics(self):
    check_metric(**vars(self))
