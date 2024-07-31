###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib import platform
from ....lib.codecs import Codec
from ....lib.common import get_media
from ....lib.gstreamer.transcoderbase import BaseTranscoderTest
from ....lib.gstreamer.util import have_gst_element

@slash.requires(*have_gst_element("vaapi"))
class TranscoderTest(BaseTranscoderTest):
  requirements = dict(
    decode = {
      Codec.AVC : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("openh264dec"), "h264parse ! openh264dec ! videoconvert"),
        hw = (platform.get_caps("decode", "avc"), have_gst_element("vaapih264dec"), "h264parse ! vaapih264dec"),
      ),
      Codec.HEVC : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("libde265dec"), "h265parse ! libde265dec ! videoconvert"),
        hw = (platform.get_caps("decode", "hevc_8"), have_gst_element("vaapih265dec"), "h265parse ! vaapih265dec"),
      ),
      Codec.MPEG2 : dict(
        sw = (dict(maxres = (2048, 2048)), have_gst_element("mpeg2dec"), "mpegvideoparse ! mpeg2dec ! videoconvert"),
        hw = (platform.get_caps("decode", "mpeg2"), have_gst_element("vaapimpeg2dec"), "mpegvideoparse ! vaapimpeg2dec"),
      ),
      Codec.MJPEG : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("jpegdec"), "jpegparse ! jpegdec"),
        hw = (platform.get_caps("decode", "jpeg"), have_gst_element("vaapijpegdec"), "jpegparse ! vaapijpegdec"),
      ),
      Codec.VC1 : dict(
        sw = (
          dict(maxres = (16384, 16384)), have_gst_element("avdec_vc1"),
          "'video/x-wmv,profile=(string)advanced'"
          ",width={width},height={height},framerate=14/1 ! avdec_vc1"
        ),
        hw = (
          platform.get_caps("decode", "vc1"), have_gst_element("vaapivc1dec"),
          "'video/x-wmv,profile=(string)advanced'"
          ",width={width},height={height},framerate=14/1 ! vaapivc1dec"
        ),
      ),
      Codec.VP9 : dict(
        hw = (platform.get_caps("decode", "vp9_8"), have_gst_element(f"vaapivp9dec"), f"vp9parse !  vaapivp9dec"),
      ),
    },
    encode = {
      Codec.AVC : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("x264enc"), "x264enc ! video/x-h264,profile=main ! h264parse"),
        hw = (platform.get_caps("encode", "avc"), have_gst_element("vaapih264enc"), "vaapih264enc ! video/x-h264,profile=main ! h264parse"),
        lp = (platform.get_caps("vdenc", "avc"), have_gst_element("vaapih264enc"), "vaapih264enc rate-control=cqp tune=low-power ! video/x-h264,profile=main ! h264parse"),
      ),
      Codec.HEVC : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("x265enc"), "videoconvert chroma-mode=none dither=0 ! video/x-raw,format=I420 ! x265enc ! video/x-h265,profile=main ! h265parse"),
        hw = (platform.get_caps("encode", "hevc_8"), have_gst_element("vaapih265enc"), "vaapih265enc ! video/x-h265,profile=main ! h265parse"),
        lp = (platform.get_caps("vdenc", "hevc_8"), have_gst_element("vaapih265enc"), "vaapih265enc tune=low-power ! video/x-h265,profile=main ! h265parse"),
      ),
      Codec.MPEG2 : dict(
        sw = (dict(maxres = (2048, 2048)), have_gst_element("avenc_mpeg2video"), "avenc_mpeg2video ! mpegvideoparse"),
        hw = (platform.get_caps("encode", "mpeg2"), have_gst_element("vaapimpeg2enc"), "vaapimpeg2enc ! mpegvideoparse"),
      ),
      Codec.MJPEG : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("jpegenc"), "jpegenc ! jpegparse"),
        hw = (platform.get_caps("vdenc", "jpeg"), have_gst_element("vaapijpegenc"), "vaapijpegenc ! jpegparse"),
      ),
      Codec.VP9 : dict(
        lp = (platform.get_caps("vdenc", "vp9_8"), have_gst_element("vaapivp9enc"), "vaapivp9enc tune=low-power ! vp9parse ! matroskamux"),
      ),
    },
    vpp = {
      "scale" : dict(
        sw = (True, have_gst_element("videoscale"), "videoscale ! video/x-raw,width={width},height={height}"),
        hw = (platform.get_caps("vpp", "scale"), have_gst_element("vaapipostproc"), "vaapipostproc ! 'video/x-raw(ANY),width={width},height={height}'"),
        lp = (platform.get_caps("vpp", "scale"), have_gst_element("vaapipostproc"), "vaapipostproc ! 'video/x-raw(ANY),width={width},height={height}'"),
      ),
    },
  )

  def before(self):
    super().before()
    os.environ["GST_VAAPI_DRM_DEVICE"] = get_media().render_device
