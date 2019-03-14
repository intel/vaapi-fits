###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ...lib.common import memoize, try_call, get_media

def using_compatible_driver():
  return get_media()._get_driver_name() == "iHD"

@memoize
def have_ffmpeg():
  return try_call("which ffmpeg")

@memoize
def have_ffmpeg_qsv_accel():
  return try_call("ffmpeg -hide_banner -hwaccels | grep qsv")

@memoize
def have_ffmpeg_h264_qsv_decode():
  return try_call("ffmpeg -hide_banner -decoders | grep h264_qsv")

@memoize
def have_ffmpeg_h264_decode():
  return try_call("ffmpeg -hide_banner -decoders | awk '{print $2}' | grep -w h264")

@memoize
def have_ffmpeg_hevc_qsv_decode():
  return try_call("ffmpeg -hide_banner -decoders | grep hevc_qsv")

@memoize
def have_ffmpeg_hevc_decode():
  return try_call("ffmpeg -hide_banner -decoders | awk '{print $2}' | grep -w hevc")

@memoize
def have_ffmpeg_mjpeg_qsv_decode():
  return try_call("ffmpeg -hide_banner -decoders | grep mjpeg_qsv")

@memoize
def have_ffmpeg_mpeg2_qsv_decode():
  return try_call("ffmpeg -hide_banner -decoders | grep mpeg2_qsv")

@memoize
def have_ffmpeg_vc1_qsv_decode():
  return try_call("ffmpeg -hide_banner -decoders | grep vc1_qsv")

@memoize
def have_ffmpeg_vp8_qsv_decode():
  return try_call("ffmpeg -hide_banner -decoders | grep vp8_qsv")

@memoize
def have_ffmpeg_vp9_qsv_decode():
  return try_call("ffmpeg -hide_banner -decoders | grep vp9_qsv")

@memoize
def have_ffmpeg_h264_qsv_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep h264_qsv")

@memoize
def have_ffmpeg_x264_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep libx264")

@memoize
def have_ffmpeg_hevc_qsv_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep hevc_qsv")

@memoize
def have_ffmpeg_x265_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep libx265")

@memoize
def have_ffmpeg_mjpeg_qsv_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep mjpeg_qsv")

@memoize
def have_ffmpeg_mjpeg_encode():
  return try_call("ffmpeg -hide_banner -encoders | awk '{print $2}' | grep -w mjpeg")

@memoize
def have_ffmpeg_mpeg2_qsv_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep mpeg2_qsv")

@memoize
def have_ffmpeg_mpeg2_encode():
  return try_call("ffmpeg -hide_banner -encoders | awk '{print $2}' | grep -w mpeg2video")

@memoize
def have_ffmpeg_filter(name):
  result = try_call("ffmpeg -hide_banner -filters | grep {}".format(name))
  return result, name

@memoize
def mapformat(format):
  return {
    "I420"  : "yuv420p",
    "NV12"  : "nv12",
    "P010"  : "p010le",
    "YUY2"  : "yuyv422",
    "422H"  : "yuv422p",
    "422V"  : "yuv440p",
    "444P"  : "yuv444p",
    "Y800"  : "gray8",
  }.get(format, None)

@memoize
def map_deinterlace_method(method):
  return {
    "bob"               : "bob",
    "advanced"          : "advanced",
  }.get(method, None)

@memoize
def mapprofile(codec, profile):
  return {
    "avc"      : {
      "high"      : "high",
      "main"      : "main",
      "baseline"  : "baseline",
      "unknown"   : "unknown"
    },
    "hevc-8"   : {
      "main"      : "main",
      "mainsp"    : "mainsp",
      "unknown"   : "unknown"
    },
    "hevc-10"  : {
      "main10"    : "main10"
    },
    "mpeg2"    : {
      "high"      : "high",
      "main"      : "main",
      "simple"    : "simple",
      "unknown"   : "unknown"
    },
    "jpeg"     : {
      "baseline"  : "baseline",
    },
  }.get(codec, {}).get(profile, None)

def load_test_spec(*ctx):
  from ...lib import get_media
  import copy

  # get copy of general ctx entries
  spec = copy.deepcopy(get_media()._get_test_spec(*ctx))

  # component specific entries override general ctx entries
  spec.update(get_media()._get_test_spec("ffmpeg-qsv", *ctx))

  return spec
