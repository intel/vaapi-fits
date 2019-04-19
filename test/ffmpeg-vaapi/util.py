###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ...lib.common import memoize, try_call

@memoize
def have_ffmpeg():
  return try_call("which ffmpeg")

@memoize
def have_ffmpeg_vaapi_accel():
  return try_call("ffmpeg -hide_banner -hwaccels | grep vaapi")

@memoize
def have_ffmpeg_h264_vaapi_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep h264_vaapi")

@memoize
def have_ffmpeg_hevc_vaapi_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep hevc_vaapi")

def have_ffmpeg_mjpeg_vaapi_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep mjpeg_vaapi")

@memoize
def have_ffmpeg_mpeg2_vaapi_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep mpeg2_vaapi")

@memoize
def have_ffmpeg_vc1_vaapi_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep vc1_vaapi")

@memoize
def have_ffmpeg_vp8_vaapi_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep vp8_vaapi")

@memoize
def have_ffmpeg_vp9_vaapi_encode():
  return try_call("ffmpeg -hide_banner -encoders | grep vp9_vaapi")

@memoize
def have_ffmpeg_filter(name):
  result = try_call("ffmpeg -hide_banner -filters | grep {}".format(name))
  return result, name

@memoize
def have_ffmpeg_encoder(encoder):
  result = try_call("ffmpeg -hide_banner -encoders | awk '{{print $2}}' | grep -w {}".format(encoder))
  return result, encoder

@memoize
def have_ffmpeg_decoder(decoder):
  result = try_call("ffmpeg -hide_banner -decoders | awk '{{print $2}}' | grep -w {}".format(decoder))
  return result, decoder

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
    "ARGB"  : "rgb32",
    "P210"  : "yuv422p10le",
    "P410"  : "yuv444p10le",
  }.get(format, None)

@memoize
def map_deinterlace_method(method):
  return {
    "bob"               : "bob",
    "weave"             : "weave",
    "motion-adaptive"   : "motion_adaptive",
    "motion-compensated": "motion_compensated",
  }.get(method, None)

@memoize
def mapprofile(codec, profile):
  return {
    "avc"      : {
      "high"                  : "high",
      "main"                  : "main",
      "constrained-baseline"  : "constrained_baseline",
    },
    "hevc-8"   : {
      "main"                  : "main",
    },
    "hevc-10"  : {
      "main10"                : "main10",
    },
    "jpeg"     : {
      "baseline"              : "baseline",
    },
    "mpeg2"    : {
      "main"                  : 4,
      "simple"                : 5,
    },
    "vp8"      : {
      "version0_3"            : "version0_3",
    },
    "vp9"      : {
      "profile0"              : "profile0",
    },
  }.get(codec, {}).get(profile, None)

def load_test_spec(*ctx):
  from ...lib import get_media
  import copy

  # get copy of general ctx entries
  spec = copy.deepcopy(get_media()._get_test_spec(*ctx))

  # component specific entries override general ctx entries
  spec.update(get_media()._get_test_spec("ffmpeg-vaapi", *ctx))

  return spec
