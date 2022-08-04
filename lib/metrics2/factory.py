###
### Copyright (C) 2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ..common import Singleton
from ..properties import PropertyHandler
from .util import get_framesize

class Metric(PropertyHandler):
  filetest  = property(lambda self: self.ifprop("filetest", "{filetest}") or self.props["decoded"])
  width     = property(lambda self: self.props["width"])
  height    = property(lambda self: self.props["height"])
  frames    = property(lambda self: self.props["frames"])
  format    = property(lambda self: self.props["format"])
  expect    = property(lambda self: self.props["metric"].get("expect", None))
  context   = property(lambda self: self.props.get("refctx", []))
  framesize = property(lambda self: get_framesize(self.width, self.height, self.format))

  def update(self, **properties):
    super().update(**properties)
    # Invalidate "actual". It needs recalculated when properties changed.
    self._actual = None

  @property # getter
  def actual(self):
    if self._actual is None:
      self.actual = self.calculate()
    return self._actual

  @actual.setter
  def actual(self, value):
    self._actual = value

  @expect.setter
  def expect(self, value):
    self.props["metric"]["expect"] = value

  def calculate(self):
    raise NotImplementedError

class MetricFactory(metaclass = Singleton):
  def __init__(self):
    self.metrics = dict()

  def register(self, metric):
    key = metric.__name__.lower()
    assert issubclass(metric, Metric), f"{metric.__name__} is not a Metric"
    assert key not in self.metrics, f"metric '{key}' is already registered"
    self.metrics[key] = metric
    return self

  def create(self, **config):
    key = config["metric"]["type"]
    metric = self.metrics[key]
    return metric(**config)

register  = MetricFactory().register
create    = MetricFactory().create
