###
### Copyright (C) 2023 Intel Corporation
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

def make_requirements():
  hwdevice = get_media().render_device.split('/')[-1]
  hw = hwdevice if hwdevice not in ['renderD128', '0'] else ""

  return dict(
    decode = {
      Codec.AVC : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("openh264dec"), "h264parse ! openh264dec ! videoconvert"),
        hw = (platform.get_caps("decode", "avc"), have_gst_element(f"va{hw}h264dec"), f"h264parse ! va{hw}h264dec"),
      ),
      Codec.HEVC : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("libde265dec"), "h265parse ! libde265dec ! videoconvert"),
        hw = (platform.get_caps("decode", "hevc_8"), have_gst_element(f"va{hw}h265dec"), f"h265parse ! va{hw}h265dec"),
      ),
      Codec.MPEG2 : dict(
        sw = (dict(maxres = (2048, 2048)), have_gst_element("mpeg2dec"), "mpegvideoparse ! mpeg2dec ! videoconvert"),
        hw = (platform.get_caps("decode", "mpeg2"), have_gst_element(f"va{hw}mpeg2dec"), f"mpegvideoparse ! va{hw}mpeg2dec"),
      ),
      Codec.MJPEG : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("jpegdec"), "jpegparse ! jpegdec"),
        hw = (platform.get_caps("decode", "jpeg"), have_gst_element(f"va{hw}jpegdec"), f"jpegparse ! va{hw}jpegdec"),
      ),
      Codec.VP9 : dict(
        hw = (platform.get_caps("decode", "vp9_8"), have_gst_element(f"va{hw}vp9dec"), f"vp9parse ! va{hw}vp9dec"),
      ),
      Codec.AV1 : dict(
        hw = (platform.get_caps("decode", "av1_8"), have_gst_element(f"va{hw}av1dec"), f"av1parse ! va{hw}av1dec"),
      ),
    },
    encode = {
      Codec.AVC : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("x264enc"), "x264enc ! video/x-h264,profile=main ! h264parse"),
        hw = (platform.get_caps("encode", "avc"), have_gst_element(f"va{hw}h264enc"), f"va{hw}h264enc ! video/x-h264,profile=main ! h264parse"),
        lp = (platform.get_caps("vdenc", "avc"), have_gst_element(f"va{hw}h264lpenc"), f"va{hw}h264lpenc ! video/x-h264,profile=main ! h264parse"),
      ),
      Codec.HEVC : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("x265enc"), "videoconvert chroma-mode=none dither=0 ! video/x-raw,format=I420 ! x265enc ! video/x-h265,profile=main ! h265parse"),
        hw = (platform.get_caps("encode", "hevc_8"), have_gst_element(f"va{hw}h265enc"), f"va{hw}h265enc ! video/x-h265,profile=main ! h265parse"),
        lp = (platform.get_caps("vdenc", "hevc_8"), have_gst_element(f"va{hw}h265lpenc"), f"va{hw}h265lpenc ! video/x-h265,profile=main ! h265parse"),
      ),
      Codec.MPEG2 : dict(
        sw = (dict(maxres = (2048, 2048)), have_gst_element("avenc_mpeg2video"), "avenc_mpeg2video ! mpegvideoparse"),
        hw = (platform.get_caps("encode", "mpeg2"), have_gst_element(f"va{hw}mpeg2enc"), f"va{hw}mpeg2enc ! mpegvideoparse"),
      ),
      Codec.MJPEG : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("jpegenc"), "jpegenc ! jpegparse"),
        hw = (platform.get_caps("vdenc", "jpeg"), have_gst_element(f"va{hw}jpegenc"), f"va{hw}jpegenc ! jpegparse"),
      ),
      Codec.VP9 : dict(
        lp = (platform.get_caps("vdenc", "vp9_8"), have_gst_element(f"va{hw}vp9lpenc"), f"va{hw}vp9lpenc ! vp9parse ! matroskamux"),
      ),
      Codec.AV1 : dict(
        lp = (platform.get_caps("vdenc", "av1_8"), have_gst_element(f"va{hw}av1lpenc"), f"va{hw}av1lpenc ! video/x-av1,profile=main ! av1parse ! matroskamux"),
      ),
    },
    vpp = {
      "scale" : dict(
        sw = (True, have_gst_element("videoscale"), "videoscale ! video/x-raw,width={width},height={height}"),
        hw = (platform.get_caps("vpp", "scale"), have_gst_element(f"va{hw}postproc"), f"va{hw}postproc" + " ! 'video/x-raw(ANY),width={width},height={height}'"),
        lp = (platform.get_caps("vpp", "scale"), have_gst_element(f"va{hw}postproc"), f"va{hw}postproc" + " ! 'video/x-raw(ANY),width={width},height={height}'"),
      ),
    },
  )

@slash.requires(*have_gst_element("va"))
class TranscoderTest(BaseTranscoderTest):
  requirements = make_requirements()
