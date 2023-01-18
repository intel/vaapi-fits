###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import slash

from ....lib import platform
from ....lib.ffmpeg.transcoderbase import BaseTranscoderTest
from ....lib.ffmpeg.util import have_ffmpeg_decoder, have_ffmpeg_encoder, have_ffmpeg_hwaccel, have_ffmpeg_filter

@slash.requires(*have_ffmpeg_hwaccel("vaapi"))
class TranscoderTest(BaseTranscoderTest):
  requirements = dict(
    # ffmpeg-vaapi HW decoders are built-in
    decode = {
      "avc" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_decoder("h264"), "h264"),
        hw = (platform.get_caps("decode", "avc"), have_ffmpeg_decoder("h264"), "h264"),
      ),
      "hevc-8" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_decoder("hevc"), "hevc"),
        hw = (platform.get_caps("decode", "hevc_8"), have_ffmpeg_decoder("hevc"), "hevc"),
      ),
      "mpeg2" : dict(
        sw = (dict(maxres = (2048, 2048)), have_ffmpeg_decoder("mpeg2video"), "mpeg2video"),
        hw = (platform.get_caps("decode", "mpeg2"), have_ffmpeg_decoder("mpeg2video"), "mpeg2video"),
      ),
      "mjpeg" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_decoder("mjpeg"), "mjpeg"),
        hw = (platform.get_caps("decode", "jpeg"), have_ffmpeg_decoder("mjpeg"), "mjpeg"),
      ),
      "vc1" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_decoder("vc1"), "vc1"),
        hw = (platform.get_caps("decode", "vc1"), have_ffmpeg_decoder("vc1"), "vc1"),
      ),
      "av1" : dict(
        hw = (platform.get_caps("decode", "av1_8"), have_ffmpeg_decoder("av1_qsv"), "av1_qsv"),
      ),
    },
    encode = {
      "avc" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_encoder("libx264"), "libx264"),
        hw = (platform.get_caps("encode", "avc"), have_ffmpeg_encoder("h264_vaapi"), "h264_vaapi"),
        lp = (platform.get_caps("vdenc", "avc"), have_ffmpeg_encoder("h264_vaapi"), "h264_vaapi -qp 20"),
      ),
      "hevc-8" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_encoder("libx265"), "libx265"),
        hw = (platform.get_caps("encode", "hevc_8"), have_ffmpeg_encoder("hevc_vaapi"), "hevc_vaapi"),
        lp = (platform.get_caps("vdenc", "hevc_8"), have_ffmpeg_encoder("hevc_vaapi"), "hevc_vaapi"),
      ),
      "mpeg2" : dict(
        sw = (dict(maxres = (2048, 2048)), have_ffmpeg_encoder("mpeg2video"), "mpeg2video"),
        hw = (platform.get_caps("encode", "mpeg2"), have_ffmpeg_encoder("mpeg2_vaapi"), "mpeg2_vaapi"),
      ),
      "mjpeg" : dict(
        sw = (dict(maxres = (16384, 16384)), have_ffmpeg_encoder("mjpeg"), "mjpeg"),
        hw = (platform.get_caps("vdenc", "jpeg"), have_ffmpeg_encoder("mjpeg_vaapi"), "mjpeg_vaapi"),
      ),
      "vp9" : dict(
        lp = (platform.get_caps("vdenc", "vp9_8"), have_ffmpeg_encoder("vp9_vaapi"), "vp9_vaapi"),
      ),
      "av1" : dict(
        lp = (platform.get_caps("vdenc", "av1_8"), have_ffmpeg_encoder("av1_vaapi"), "av1_vaapi"),
      ),
    },
    vpp = {
      "scale" : dict(
        sw = (True, have_ffmpeg_filter("scale"), "scale=w={width}:h={height}"),
        hw = (platform.get_caps("vpp", "scale"), have_ffmpeg_filter("scale_vaapi"), "scale_vaapi=w={width}:h={height}"),
        lp = (platform.get_caps("vpp", "scale"), have_ffmpeg_filter("scale_vaapi"), "scale_vaapi=w={width}:h={height}"),
      ),
    },
  )

  # hevc implies hevc 8 bit
  requirements["encode"]["hevc"] = requirements["encode"]["hevc-8"]
  requirements["decode"]["hevc"] = requirements["decode"]["hevc-8"]

  def before(self):
    super().before()
    self.hwaccel = "vaapi"
