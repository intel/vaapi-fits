###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib.common import memoize
from ....lib.formats import match_best_format
from ....lib.gstreamer.util import *

def get_supported_format_map():
  #The map first entry is for gst element properties;the second entry is for gst caps filters
  #    i420 is entry for gst properties such as vapostproc
  #    I420: is entry for gst caps filter
  return {
    "I420"  : ("i420", "I420"),
    "NV12"  : ("nv12", "NV12"),
    "YV12"  : ("yv12", "YV12"),
    "AYUV"  : ("vuya", "VUYA"), #we use microsoft's definition of AYUV,https://docs.microsoft.com/en-us/windows/win32/medfound/recommended-8-bit-yuv-formats-for-video-rendering#ayuv
    "YUY2"  : ("yuy2", "YUY2"),
    "ARGB"  : ("argb", "ARGB"),
    "BGRA"  : ("bgra", "BGRA"),
    "422H"  : ("y42b", "Y42B"),
    "444P"  : ("y444", "Y444"),
    "P010"  : ("p010-10le", "P010_10LE"),
    "P012"  : ("p012-le", "P012_LE"),
    "I010"  : ("i420-10le", "I420_10LE"),
    "Y210"  : ("y210", "Y210"),
    "Y212"  : ("y212-le", "Y212_LE"),
    "Y410"  : ("y410", "Y410"),
    "Y412"  : ("y412", "Y412_LE"),
  }

@memoize
def mapformat(format):
  return get_supported_format_map().get(format, (None, None))[0]

@memoize
def mapformatu(format):
  return get_supported_format_map().get(format, (None, None))[1]

def map_best_hw_format(format, hwformats):
  return mapformatu(
    match_best_format(
      format, set(hwformats) & set(get_supported_format_map().keys())))

@memoize
def map_transpose_direction(degrees, method):
  return {
    (  0,         None) : "identity",
    (  0,   "vertical") : "vert",
    (  0, "horizontal") : "horiz",
    ( 90,         None) : "90r",
    ( 90,   "vertical") : "ur-ll",
    ( 90, "horizontal") : "ul-lr",
    (180,         None) : "180",
    (180,   "vertical") : "horiz",
    (180, "horizontal") : "vert",
    (270,         None) : "90l",
    (270,   "vertical") : "ul-lr",
    (270, "horizontal") : "ur-ll",
  }.get((degrees, method), None)

@memoize
def mapprofile(codec, profile):
  return {
    "avc"       : {
      "high"                  : "high",
      "main"                  : "main",
      "baseline"              : "baseline",
      "constrained-baseline"  : "constrained-baseline",
      "multiview-high"        : "multiview-high",
      "stereo-high"           : "stereo-high",
    },
    "hevc-8"    : {
      "main"                  : "main",
      "scc"                   : "screen-extended-main",
      "scc-444"               : "screen-extended-main-444",
      "main444"               : "main-444",
    },
  }.get(codec, {}).get(profile, None)

def load_test_spec(*ctx):
  from ....lib import util as libutil
  return libutil.load_test_spec("gst-va", *ctx)
