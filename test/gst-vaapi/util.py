###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ...lib.common import memoize, try_call

@memoize
def have_gst():
  return try_call("which gst-launch-1.0") and try_call("which gst-inspect-1.0")

@memoize
def have_gst_element(element):
  result = try_call("gst-inspect-1.0 {}".format(element))
  return result, element

@memoize
def mapformat(format):
  return {
    "I420"  : "i420",
    "NV12"  : "nv12",
    "YV12"  : "yv12",
    "P010"  : "p010-10le",
    "AYUV"  : "ayuv",
    "YUY2"  : "yuy2",
    "ARGB"  : "argb",
    "BGRA"  : "bgra",
    "422H"  : "y42b",
    "444P"  : "y444",
    "P210"  : "i422_10le",
    "P410"  : "y444_10le",
  }.get(format, None)

@memoize
def mapformatu(format):
  return {
    "I420"  : "I420",
    "NV12"  : "NV12",
    "YV12"  : "YV12",
    "P010"  : "P010_10LE",
    "AYUV"  : "AYUV",
    "YUY2"  : "YUY2",
    "ARGB"  : "ARGB",
    "BGRA"  : "BGRA",
    "422H"  : "Y42B",
    "444P"  : "Y444",
    "P210"  : "I422_10LE",
    "P410"  : "Y444_10LE",
  }.get(format, None)


@memoize
def map_deinterlace_method(method):
  from ...lib import get_media
  return {
    "iHD" : {
      "bob"               : "bob",
      "motion-adaptive"   : "motion-adaptive",
    },
    "i965" : {
      "bob"               : "bob",
      "motion-adaptive"   : "motion-adaptive",
      "motion-compensated": "motion-compensated",
    },
  }.get(get_media()._get_driver_name(), {}).get(method, None)

@memoize
def map_vpp_mirroring(method):
  return {
    "identity"    : "identity",
    "none"        : "identity",
    "horizontal"  : "horiz",
    "vertical"    : "vert",
  }.get(method, None)

@memoize
def map_vpp_rotation(degrees):
  return {
    0   : "identity",
    90  : "90r",
    180 : "180",
    270 : "90l",
  }.get(degrees, None)

@memoize
def map_vpp_transpose(degrees, method):
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
    "avc"      : {
      "high"                  : "high",
      "main"                  : "main",
      "baseline"              : "baseline",
      "constrained-baseline"  : "constrained-baseline",
      "multiview-high"        : "multiview-high",
      "stereo-high"           : "stereo-high",
    },
    "hevc-8"   : {
      "main"                  : "main",
    },
    "hevc-10"  : {
      "main10"                : "main-10",
    },
    "jpeg"     : {
      "baseline"              : "baseline",
    },
    "mpeg2"    : {
      "simple"                : "simple",
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
  spec.update(get_media()._get_test_spec("gst-vaapi", *ctx))

  return spec
