###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ...lib.common import memoize, try_call, call

@memoize
def have_gst():
  return try_call("which gst-launch-1.0") and try_call("which gst-inspect-1.0")

@memoize
def have_gst_element(element):
  result = try_call("gst-inspect-1.0 {}".format(element))
  return result, element

def gst_discover(filename):
  return call("gst-discoverer-1.0 {}".format(filename))
