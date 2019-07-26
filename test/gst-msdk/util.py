###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ...lib.common import memoize, try_call, get_media

def using_compatible_driver():
  return get_media()._get_driver_name() == "iHD"

@memoize
def have_gst():
  return try_call("which gst-launch-1.0") and try_call("which gst-inspect-1.0")

@memoize
def have_gst_element(element):
  result = try_call("gst-inspect-1.0 {}".format(element))
  return result, element

@memoize
def mapsubsampling(format_subsampling):
  return {
    "FORMATS_400" : ["Y800"],
    "FORMATS_420" : ["I420", "NV12", "YV12"],
    "FORMATS_422" : ["422H", "422V", "YUY2"],
    "FORMATS_444" : ["444P", "AYUV"],
  }.get(format_subsampling, [])

@memoize
def mapformat_hwup(format):
  from ...lib import get_media
  fmt = {
    "iHD" : {
      "I420"  : "NV12",
      "AYUV"  : "NV12",
      "YUY2"  : "NV12",
      "YV12"  : "NV12",
    },
  }.get(get_media()._get_driver_name(), {}).get(format, format)

  return mapformatu(fmt)

# alias
maphwformat = mapformat_hwup

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
def map_vpp_mirroring(method):
  return {
    "horizontal"  : 1,
    "vertical"    : 2,
    None          : 0,
  }.get(method, None)

@memoize
def map_deinterlace_method(method):
  return {
    "bob"              : "bob",
    "advanced"         : "advanced",
    "advanced-no-ref"  : "advanced-no-ref",
    "advanced-scd"     : "advanced-scd",
    "weave"            : "field-weave",
    "none"             : "none"
  }.get(method, None)

@memoize
def mapprofile(codec,profile):
  return {
    "avc"     : {
      "high"                  : "high",
      "main"                  : "main",
      "baseline"              : "baseline",
      "constrained-baseline"  : "constrained-baseline",
    },
    "hevc-8"  : {
      "main"                  : "main",
    },
    "hevc-10" : {
      "main10"                : "main-10",
    },
    "jpeg"     : {
      "baseline"              : "baseline",
    },
    "mpeg2"   : {
      "high"                  : "high",
      "main"                  : "main",
      "simple"                : "simple",
    },
    "vp8"      : {
      "version0_3"            : "version0_3",
    },
    "vp9"      : {
      "profile0"            : "0",
      "profile2"            : "2",
    },
  }.get(codec, {}).get(profile, None)

def load_test_spec(*ctx):
  from ...lib import get_media
  import copy

  # get copy of general ctx entries
  spec = copy.deepcopy(get_media()._get_test_spec(*ctx))

  # component specific entries override general ctx entries
  spec.update(get_media()._get_test_spec("gst-msdk", *ctx))

  return spec
