###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib.common import memoize, try_call
from ....lib.formats import match_best_format

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
    "P012"  : "p012",
    "I010"  : "yuv420p10le",
    "YUY2"  : "yuyv422",
    "422H"  : "yuv422p",
    "422V"  : "yuv440p",
    "444P"  : "yuv444p",
    "Y800"  : "gray8",
    "ARGB"  : "rgb32",
    "BGRA"  : "bgra",
    "Y210"  : "y210",
    "Y212"  : "y212",
    "Y410"  : "y410",
    "Y412"  : "y412",
    "AYUV"  : "0yuv", # 0yuv is same as microsoft AYUV except the alpha channel
  }

@memoize
def mapformat(format):
  return get_supported_format_map().get(format, None)

def map_best_hw_format(format, hwformats):
  return mapformat(
    match_best_format(
      format, set(hwformats) & set(get_supported_format_map().keys())))

@memoize
def map_deinterlace_method(method):
  from ....lib import get_media
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
    (  0,   "vertical") : "vflip",
    (  0, "horizontal") : "hflip",
    ( 90,         None) : "clock",
    ( 90,   "vertical") : "clock_flip",
    ( 90, "horizontal") : "cclock_flip",
    (180,         None) : "reversal",
    (180,   "vertical") : "hflip",
    (180, "horizontal") : "vflip",
    (270,         None) : "cclock",
    (270,   "vertical") : "cclock_flip",
    (270, "horizontal") : "clock_flip",
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
      "scc"                   : "scc",
      "scc-444"               : "scc",
    },
    "hevc-10"  : {
      "main10"                : "main10",
    },
    "hevc-12" : {
      "main12"                : "main-12",
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
    "vp9-12"      : {
      "profile3"              : "profile3",
    },
    "av1-8"   : {
      "main"                  : "main",
    },
  }.get(codec, {}).get(profile, None)

def load_test_spec(*ctx):
  from ....lib import get_media
  import copy

  # get copy of general ctx entries
  spec = copy.deepcopy(get_media()._get_test_spec(*ctx))

  # component specific entries override general ctx entries
  spec.update(get_media()._get_test_spec("ffmpeg-vaapi", *ctx))

  return spec

def get_hardware_render():
  import subprocess
  result, renderDevice = subprocess.getstatusoutput('ls /dev/dri/renderD1*|head -n 1')
  if result:
    return renderDevice
  return '/dev/dri/renderD128'
