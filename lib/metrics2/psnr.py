###
### Copyright (C) 2018-2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

try:
  # try skimage >= 0.16, first
  from skimage.metrics import peak_signal_noise_ratio as skimage_psnr
except:
  from skimage.measure import compare_psnr as skimage_psnr

from ..common import get_media, timefn
from ..formats import get_bit_depth
from .util import RawFileFrameReader, RawMetricAggregator, MetricWithDataRange
from . import factory

@timefn("psnr:calculate")
def calculate(filetrue, filetest, width, height, frames, fmttrue, fmttest):
  bitdepth = get_bit_depth(fmttrue)
  assert get_bit_depth(fmttest) == bitdepth

  return RawMetricAggregator(min).calculate(
    RawFileFrameReader(filetrue, width, height, frames, fmttrue),
    RawFileFrameReader(filetest, width, height, frames, fmttest),
    frames, MetricWithDataRange(compare_planes, bitdepth))

def compare_planes(planes, data_range = None):
  a, b = planes
  if (a == b).all():
    # Avoid "Warning: divide by zero encountered in double_scalars" generated
    # by skimage.measure.compare_psnr when a and b are exactly the same.
    return 100
  return skimage_psnr(a, b, data_range = data_range)

def compare_actual(k, ref, actual):
  assert ref is not None, "Invalid reference value"
  assert all(map(lambda r,a: a > (r * 0.98), ref[3:], actual[3:]))

class PSNR(factory.Metric):
  filetrue  = property(lambda self: self.ifprop("filetrue", "{filetrue}") or self.props["reference"])
  compare   = property(lambda self: self.props.get("compare", compare_actual))

  def calculate(self):
    return calculate(
      self.filetrue, self.filetest, self.width, self.height,
      self.frames, self.format, self.format)

  def check(self):
    get_media().baseline.check_result(
      psnr = self.actual, compare = self.compare, context = self.context)

factory.register(PSNR)
