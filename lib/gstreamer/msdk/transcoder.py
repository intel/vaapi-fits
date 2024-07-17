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
from ....lib.gstreamer.msdk.util import using_compatible_driver

@slash.requires(*have_gst_element("msdk"))
@slash.requires(using_compatible_driver)
class TranscoderTest(BaseTranscoderTest):
  requirements = dict(
    decode = {
      Codec.AVC : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("openh264dec"), "h264parse ! openh264dec ! videoconvert"),
        hw = (platform.get_caps("decode", "avc"), have_gst_element("msdkh264dec"), "h264parse ! msdkh264dec"),
        va_hw = (platform.get_caps("decode", "avc"), have_gst_element("vah264dec"), "h264parse ! vah264dec"),
        d3d11_hw = (platform.get_caps("decode", "avc"), have_gst_element("d3d11h264dec"), "h264parse ! d3d11h264dec"),
        dma = (platform.get_caps("decode", "avc"), have_gst_element("msdkh264dec"), "h264parse ! msdkh264dec ! \"video/x-raw(memory:DMABuf)\""),
      ),
      Codec.HEVC : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("libde265dec"), "h265parse ! libde265dec ! videoconvert"),
        hw = (platform.get_caps("decode", "hevc_8"), have_gst_element("msdkh265dec"), "h265parse ! msdkh265dec"),
        va_hw = (platform.get_caps("decode", "hevc_8"), have_gst_element("vah265dec"), "h265parse ! vah265dec"),
        d3d11_hw = (platform.get_caps("decode", "hevc_8"), have_gst_element("d3d11h265dec"), "h265parse ! d3d11h265dec"),
        dma = (platform.get_caps("decode", "hevc_8"), have_gst_element("msdkh265dec"), "h265parse ! msdkh265dec ! \"video/x-raw(memory:DMABuf)\""),
      ),
      Codec.MPEG2 : dict(
        sw = (dict(maxres = (2048, 2048)), have_gst_element("mpeg2dec"), "mpegvideoparse ! mpeg2dec ! videoconvert"),
        hw = (platform.get_caps("decode", "mpeg2"), have_gst_element("msdkmpeg2dec"), "mpegvideoparse ! msdkmpeg2dec"),
      ),
      Codec.MJPEG : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("jpegdec"), "jpegparse ! jpegdec"),
        hw = (platform.get_caps("decode", "jpeg"), have_gst_element("msdkmjpegdec"), "jpegparse ! msdkmjpegdec"),
      ),
      Codec.VC1 : dict(
        sw = (
          dict(maxres = (16384, 16384)), have_gst_element("avdec_vc1"),
          "'video/x-wmv,profile=(string)advanced'"
          ",width={width},height={height},framerate=14/1 ! avdec_vc1"
        ),
        hw = (
          platform.get_caps("decode", "vc1"), have_gst_element("msdkvc1dec"),
          "'video/x-wmv,profile=(string)advanced'"
          ",width={width},height={height},framerate=14/1 ! msdkvc1dec"
        ),
      ),
      Codec.VP9 : dict(
        hw = (platform.get_caps("decode", "vp9_8"), have_gst_element(f"msdkvp9dec"), f"matroskademux ! vp9parse !  msdkvp9dec"),
      ),
    },
    encode = {
      Codec.AVC : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("x264enc"), "x264enc ! video/x-h264,profile=main ! h264parse"),
        hw = (platform.get_caps("encode", "avc"), have_gst_element("msdkh264enc"), "msdkh264enc ! video/x-h264,profile=main ! h264parse"),
        lp = (platform.get_caps("vdenc", "avc"), have_gst_element("msdkh264enc"), "msdkh264enc rate-control=cqp tune=low-power ! video/x-h264,profile=main ! h264parse"),
      ),
      Codec.HEVC : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("x265enc"), "videoconvert chroma-mode=none dither=0 ! video/x-raw,format=I420 ! x265enc ! video/x-h265,profile=main ! h265parse"),
        hw = (platform.get_caps("encode", "hevc_8"), have_gst_element("msdkh265enc"), "msdkh265enc ! h265parse"),
        lp = (platform.get_caps("vdenc", "hevc_8"), have_gst_element("msdkh265enc"), "msdkh265enc tune=low-power ! h265parse"),
      ),
      Codec.MPEG2 : dict(
        sw = (dict(maxres = (2048, 2048)), have_gst_element("avenc_mpeg2video"), "avenc_mpeg2video ! mpegvideoparse"),
        hw = (platform.get_caps("encode", "mpeg2"), have_gst_element("msdkmpeg2enc"), "msdkmpeg2enc ! mpegvideoparse"),
      ),
      Codec.MJPEG : dict(
        sw = (dict(maxres = (16384, 16384)), have_gst_element("jpegenc"), "jpegenc ! jpegparse"),
        hw = (platform.get_caps("vdenc", "jpeg"), have_gst_element("msdkmjpegenc"), "msdkmjpegenc ! jpegparse"),
      ),
      Codec.VP9 : dict(
        lp = (platform.get_caps("vdenc", "vp9_8"), have_gst_element("msdkvp9enc"), "msdkvp9enc ! vp9parse ! matroskamux"),
      ),
    },
    vpp = {
      "scale" : dict(
        sw = (True, have_gst_element("videoscale"), "videoscale ! video/x-raw,width={width},height={height}"),
        hw = (platform.get_caps("vpp", "scale"), have_gst_element("msdkvpp"), "msdkvpp hardware=true scaling-mode=1 ! 'video/x-raw(ANY),format={format},width={width},height={height}'"),
        lp = (platform.get_caps("vpp", "scale"), have_gst_element("msdkvpp"), "msdkvpp hardware=true scaling-mode=1 ! 'video/x-raw(ANY),format={format},width={width},height={height}'"),
      ),
    },
  )

  def before(self):
    super().before()
    os.environ["GST_MSDK_DRM_DEVICE"] = get_media().render_device

    # The msdk plugins have rank "none (0)".  Thus, they will be skipped by the
    # gst-discoverer.  If there are no alternative plugins, then gst-discoverer
    # will fail.  Thus, temporarily change the msdk decode plugins rank to
    # "primary (256)" so they can be used in gst-discoverer
    self.__rank_before = os.environ.get("GST_PLUGIN_FEATURE_RANK", None)
    ranks = [] if self.__rank_before is None else self.__rank_before.split(',')
    ranks += [
      "msdkh264dec:primary",
      "msdkh265dec:primary",
      "msdkmpeg2dec:primary",
      "msdkmjpegdec:primary",
    ]
    os.environ["GST_PLUGIN_FEATURE_RANK"] = ','.join(ranks)

  def after(self):
    super().after()

    if None == self.__rank_before:
      del os.environ["GST_PLUGIN_FEATURE_RANK"]
    else:
      os.environ["GST_PLUGIN_FEATURE_RANK"] = self.__rank_before
