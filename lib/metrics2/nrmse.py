###
### Copyright (C) 2018-2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

try:
  # try skimage >= 0.16, first
  from skimage.metrics import normalized_root_mse as skimage_nrmse
except:
  from skimage.measure import compare_nrmse as skimage_nrmse

from ..common import get_media, timefn
from .util import RawFileFrameReader, RawMetricAggregator
from . import factory

@timefn("nrmse:calculate")
def calculate(filetrue, filetest, width, height, frames, format):
  return RawMetricAggregator(max).calculate(
    RawFileFrameReader(filetrue, width, height, frames, format),
    RawFileFrameReader(filetest, width, height, frames, format),
    frames, compare)

def compare(planes):
  a, b = planes
  return skimage_nrmse(a, b)

class NRMSE(factory.Metric):
  filetrue  = property(lambda self: self.ifprop("filetrue", "{filetrue}") or self.props["reference"])
  avgrange  = property(lambda self: self.props["metric"].get("avg_range", [(0, 0.07)] * 3))

  def calculate(self):
    return calculate(
      self.filetrue, self.filetest, self.width, self.height,
      self.frames, self.format)

  def check(self):
    get_media()._set_test_details(nrmse = self.actual)
    assert self.avgrange[0][0] <= self.actual[-3] <= self.avgrange[0][1]
    assert self.avgrange[1][0] <= self.actual[-2] <= self.avgrange[1][1]
    assert self.avgrange[2][0] <= self.actual[-1] <= self.avgrange[2][1]

factory.register(NRMSE)
