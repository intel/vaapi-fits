###
### Copyright (C) 2018-2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

try:
  # try skimage >= 0.16, first
  from skimage.metrics import structural_similarity as skimage_ssim
except:
  from skimage.measure import compare_ssim as skimage_ssim

from ..common import get_media, timefn
from ..formats import PixelFormat
from .util import RawFileFrameReader, RawMetricAggregator, MetricWithDataRange
from . import factory

@timefn("ssim:calculate")
def calculate(filetrue, filetest, width, height, frames, fmttrue, fmttest):
  bitdepth = PixelFormat(fmttrue).bitdepth
  assert PixelFormat(fmttest).bitdepth == bitdepth

  return RawMetricAggregator(min).calculate(
    RawFileFrameReader(filetrue, width, height, frames, fmttrue),
    RawFileFrameReader(filetest, width, height, frames, fmttest),
    frames, MetricWithDataRange(compare, bitdepth))

def compare(planes, data_range = None):
  a, b = planes
  if a is None or b is None: # handle Y800 case
    return 1.0
  return skimage_ssim(a, b, win_size = 3, data_range = data_range)

class SSIM(factory.Metric):
  format    = property(lambda self: self.props.get("format2", super().format))
  filetrue  = property(lambda self: self.ifprop("filetrue", "{filetrue}") or self.props["reference"])
  fmttrue   = property(lambda self: super().format)
  miny      = property(lambda self: self.props["metric"].get("miny", 1.0))
  minu      = property(lambda self: self.props["metric"].get("minu", 1.0))
  minv      = property(lambda self: self.props["metric"].get("minv", 1.0))

  def calculate(self):
    return calculate(
      self.filetrue, self.filetest, self.width, self.height,
      self.frames, self.fmttrue, self.format)

  def check(self):
    get_media()._set_test_details(ssim = self.actual)
    assert 1.0 >= self.actual[0] >= self.miny
    assert 1.0 >= self.actual[1] >= self.minu
    assert 1.0 >= self.actual[2] >= self.minv

factory.register(SSIM)
