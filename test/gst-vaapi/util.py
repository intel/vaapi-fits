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
def have_gst_vaapi():
  return try_call("gst-inspect-1.0 vaapi")

@memoize
def have_gst_vaapih264dec():
  return try_call("gst-inspect-1.0 vaapih264dec")

@memoize
def have_gst_vaapih265dec():
  return try_call("gst-inspect-1.0 vaapih265dec")

@memoize
def have_gst_vaapijpegdec():
  return try_call("gst-inspect-1.0 vaapijpegdec")

@memoize
def have_gst_vaapimpeg2dec():
  return try_call("gst-inspect-1.0 vaapimpeg2dec")

@memoize
def have_gst_vaapivc1dec():
  return try_call("gst-inspect-1.0 vaapivc1dec")

@memoize
def have_gst_vaapivp8dec():
  return try_call("gst-inspect-1.0 vaapivp8dec")

@memoize
def have_gst_vaapivp9dec():
  return try_call("gst-inspect-1.0 vaapivp9dec")

@memoize
def have_gst_vaapih264enc():
  return try_call("gst-inspect-1.0 vaapih264enc")

@memoize
def have_gst_vaapih265enc():
  return try_call("gst-inspect-1.0 vaapih265enc")

@memoize
def have_gst_vaapijpegenc():
  return try_call("gst-inspect-1.0 vaapijpegenc")

@memoize
def have_gst_vaapimpeg2enc():
  return try_call("gst-inspect-1.0 vaapimpeg2enc")

@memoize
def have_gst_vaapivc1enc():
  return try_call("gst-inspect-1.0 vaapivc1enc")

@memoize
def have_gst_vaapivp8enc():
  return try_call("gst-inspect-1.0 vaapivp8enc")

@memoize
def have_gst_vaapipostproc():
  return try_call("gst-inspect-1.0 vaapipostproc")

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
  }.get(format, None)


@memoize
def map_deinterlace_method(method):
  return {
    "bob"               : "bob",
    "weave"             : "weave",
    "motion-adaptive"   : "motion-adaptive",
    "motion-compensated": "motion-compensated",
    "none"              : "none"
  }.get(method, None)

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
  }.get(codec, {}).get(profile, None)

def load_test_spec(*ctx):
  from ...lib import get_media
  import copy

  # get copy of general ctx entries
  spec = copy.deepcopy(get_media()._get_test_spec(*ctx))

  # component specific entries override general ctx entries
  spec.update(get_media()._get_test_spec("gst-vaapi", *ctx))

  return spec
