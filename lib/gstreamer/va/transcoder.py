###
### Copyright (C) 2022-2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib import platform
from ....lib.common import get_media
from ....lib.gstreamer.transcoderbase import BaseTranscoderTest
from ....lib.gstreamer.util import have_gst_element

@slash.requires(*have_gst_element("va"))
class TranscoderTest(BaseTranscoderTest):
  requirements = dict(
    decode = {
      "avc" : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("openh264dec"), "h264parse ! openh264dec ! videoconvert"),
        hw = (platform.get_caps("decode", "avc"), have_gst_element("vah264dec"), "h264parse ! vah264dec"),
      ),
      "hevc-8" : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("libde265dec"), "h265parse ! libde265dec ! videoconvert"),
        hw = (platform.get_caps("decode", "hevc_8"), have_gst_element("vah265dec"), "h265parse ! vah265dec"),
      ),
      "mpeg2" : dict(
        sw = (dict(maxres = (2048, 2048)), have_gst_element("mpeg2dec"), "mpegvideoparse ! mpeg2dec ! videoconvert"),
        hw = (platform.get_caps("decode", "mpeg2"), have_gst_element("vampeg2dec"), "mpegvideoparse ! vampeg2dec"),
      ),
      "mjpeg" : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("jpegdec"), "jpegparse ! jpegdec"),
        hw = (platform.get_caps("decode", "jpeg"), have_gst_element("vajpegdec"), "jpegparse ! vajpegdec"),
      ),
      "vc1" : dict(
        sw = (
          dict(maxres = (16384, 16384)), have_gst_element("avdec_vc1"),
          "'video/x-wmv,profile=(string)advanced'"
          ",width={width},height={height},framerate=14/1 ! avdec_vc1"
        ),
        hw = (
          platform.get_caps("decode", "vc1"), have_gst_element("vavc1dec"),
          "'video/x-wmv,profile=(string)advanced'"
          ",width={width},height={height},framerate=14/1 ! vavc1dec"
        ),
      ),
    },
    encode = {
      "avc" : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("x264enc"), "x264enc ! video/x-h264,profile=main ! h264parse"),
        hw = (platform.get_caps("encode", "avc"), have_gst_element("vah264enc"), "vah264enc ! video/x-h264,profile=main ! h264parse"),
        lp = (platform.get_caps("vdenc", "avc"), have_gst_element("vah264lpenc"), "vah264lpenc rate-control=cqp ! video/x-h264,profile=main ! h264parse"),
      ),
      "hevc-8" : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("x265enc"), "videoconvert chroma-mode=none dither=0 ! video/x-raw,format=I420 ! x265enc ! video/x-h265,profile=main ! h265parse"),
        hw = (platform.get_caps("encode", "hevc_8"), have_gst_element("vah265enc"), "vah265enc ! video/x-h265,profile=main ! h265parse"),
        lp = (platform.get_caps("vdenc", "hevc_8"), have_gst_element("vah265lpenc"), "vah265lpenc ! video/x-h265,profile=main ! h265parse"),
      ),
      "mjpeg" : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("jpegenc"), "jpegenc ! jpegparse"),
        hw = (platform.get_caps("vdenc", "jpeg"), have_gst_element("vajpegenc"), "vajpegenc ! jpegparse"),
      ),
    },
    vpp = {
      "scale" : dict(
        sw = (True, have_gst_element("videoscale"), "videoscale ! video/x-raw,width={width},height={height}"),
        hw = (platform.get_caps("vpp", "scale"), have_gst_element("vapostproc"), "vapostproc ! video/x-raw,width={width},height={height}"),
      ),
    },
  )

  # hevc implies hevc 8 bit
  requirements["encode"]["hevc"] = requirements["encode"]["hevc-8"]
  requirements["decode"]["hevc"] = requirements["decode"]["hevc-8"]

