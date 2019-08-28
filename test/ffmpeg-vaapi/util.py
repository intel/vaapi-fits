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
def have_ffmpeg_filter(name):
  result = try_call("ffmpeg -hide_banner -filters | awk '{{print $2}}' | grep -w {}".format(name))
  return result, name

@memoize
def have_ffmpeg_encoder(encoder):
  result = try_call("ffmpeg -hide_banner -encoders | awk '{{print $2}}' | grep -w {}".format(encoder))
  return result, encoder

@memoize
def have_ffmpeg_decoder(decoder):
  result = try_call("ffmpeg -hide_banner -decoders | awk '{{print $2}}' | grep -w {}".format(decoder))
  return result, decoder

def get_supported_format_map():
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
  }

@memoize
def mapformat(format):
  return get_supported_format_map().get(format, None)

@memoize
def map_deinterlace_method(method):
  from ...lib import get_media
  return {
    "iHD" : {
      "bob"               : "bob",
      "motion-adaptive"   : "motion_adaptive",
    },
    "i965" : {
      "bob"               : "bob",
      "motion-adaptive"   : "motion_adaptive",
      "motion-compensated": "motion_compensated",
    },
  }.get(get_media()._get_driver_name(), {}).get(method, None)

@memoize
def map_transpose_direction(degrees, method):
  return {
    (270,   "vertical")   : "cclock_flip",
    ( 90,         None)   : "clock",
    (270,         None)   : "cclock",
    ( 90,   "vertical")   : "clock_flip",
    (180,         None)   : "reversal",
    (  0, "horizontal")   : "hflip",
    (  0,   "vertical")   : "vflip",
  }.get( (degrees, method), None)

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
