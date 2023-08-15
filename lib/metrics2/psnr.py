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

import math
import os
import statistics

from ..common import get_media, timefn
from ..formats import get_bit_depth
from .util import RawFileFrameReader, RawMetricAggregator, MetricWithDataRange
from . import factory

trend_models = dict(
  power   = lambda x, a, k: a*x**k,
  powern  = lambda x, a, k: a*x**-k,
  powerc  = lambda x, a, k, c: a*x**k + c,
  powernc = lambda x, a, k, c: a*x**-k + c,
  cubic   = lambda x, a, b, c, d: d*x**3 + c*x**2 + b*x + a,
  quartic = lambda x, a, b, c, d, e: e*x**4 + d*x**3 + c*x**2 + b*x + a,
)

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

def compare_ge(k, ref, actual):
  assert ref is not None, "Invalid reference value"
  assert actual >= ref

class PSNR(factory.Metric):
  filetrue  = property(lambda self: self.ifprop("filetrue", "{filetrue}") or self.props["reference"])
  compare   = property(lambda self: self.props.get("compare", compare_actual))
  mode      = property(lambda self: self.props["metric"].get("mode", "default"))

  # mode = trendline
  tolerance = property(lambda self: self.props["metric"].get("tolerance", 5.0))
  filecoded = property(lambda self: self.ifprop("filecoded", "{filecoded}") or self.props["encoder"].encoded)
  codedsize = property(lambda self: os.path.getsize(self.filecoded)) # bytes
  rawsize   = property(lambda self: self.framesize * self.frames) # bytes
  compratio = property(lambda self: self.rawsize / self.codedsize)
  logratio  = property(lambda self: math.log(self.compratio))
  average   = property(lambda self: statistics.mean(self.actual[-3:]))

  def calculate(self):
    return calculate(
      self.filetrue, self.filetest, self.width, self.height,
      self.frames, self.format, self.format)

  def check(self):
    if self.mode == "trendline":
      self.check_trendline()
    else:
      get_media().baseline.check_result(
        psnr = self.actual, compare = self.compare, context = self.context)

  def check_trendline(self):
    gopkey = 30 if self.props.get("gop", 30) > 1 else 1
    model = get_media().baseline.lookup(
      f"model/encode/{self.props['codec']}"
      f":trend.test(case={self.props['case']})", f"gop.{gopkey}")

    assert model is not None, "Trendline model reference not found"

    fname = model["fx"]
    fopts = model["popt"]
    get_media()._set_test_details(**{
      "size:raw"          : self.rawsize,
      "compression:ratio" : self.compratio,
      "compression:log"   : self.logratio,
      "model:trend:name"  : fname,
      "model:trend:opts"  : fopts,
      "psnr:stats"        : self.actual,
      "psnr:tolerance"    : self.tolerance,
    })

    fx = trend_models[fname]
    expect = max(20.0, fx(self.logratio, *fopts) - self.tolerance)

    get_media().baseline.check_result(
      psnr = self.average, reference = {"psnr" : expect}, compare = compare_ge)

factory.register(PSNR)
