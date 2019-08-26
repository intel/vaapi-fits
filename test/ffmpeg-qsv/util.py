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
    "motion-adaptive"   : "advanced", # aka
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
  }.get(codec, {}).get(profile, None)

def load_test_spec(*ctx):
  from ...lib import get_media
  import copy

  # get copy of general ctx entries
  spec = copy.deepcopy(get_media()._get_test_spec(*ctx))

  # component specific entries override general ctx entries
  spec.update(get_media()._get_test_spec("ffmpeg-qsv", *ctx))

  return spec
