###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ...lib import *
from ...lib import metrics2
from ...lib.metrics2.psnr import trend_models
from ...lib.codecs import Codec
from ...lib.formats import PixelFormat

import itertools
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.optimize import curve_fit

plt.rcParams['figure.figsize'] = [25, 15]

class TrendModelMixin:
  @classmethod
  def filter_spec(cls, spec):
    def has_trend_metric(val):
      metric = val.get("metric", dict())
      return (
        metric.get("type", None) == "psnr" and
        metric.get("mode", None) == "trendline"
      )
    return "case", [k for k,v in spec.items() if has_trend_metric(v)]

  def initvars(self, default_profile):
    vars(self).update(
      rcmode  = "cqp",
      bframes = 2,
      quality = 4,
      iqfactor = 1,
      bqfactor = 1,
      iqoffset = 0,
      bqoffset = 0,
    )
    vars(self).setdefault("profile", default_profile)
    vars(self).setdefault("modelqps", [1, 2, 4, 7, 10, 13, 16, 23, 31, 40, 42, 45, 48, 49, 51])
    vars(self).setdefault("modelfns", ["cubic", "powernc", "powerc", "powern", "power"])

  def fit(self):
    self.initvars("main")

    platform = get_media()._get_platform_name()
    tolerance = vars(self).get("metric", dict()).get("tolerance", 5.0)

    # FIXME(WA): temporary workaround during Codec enum refactor to maintain
    # backwards compatibility for the legacy "<codec>-<bitrate>" lookup keys
    codec = Codec(self.codec)
    bitdepth = PixelFormat(self.format).bitdepth
    if not codec.endswith(f"-{bitdepth}"):
      if codec in [Codec.HEVC, Codec.AV1]:
        codec += f"-{bitdepth}"
      elif codec in [Codec.VP9] and 8 != bitdepth:
        codec += f"-{bitdepth}"

    get_media().baseline.update_reference(
      driver = get_media()._get_driver_name(),
      platform = platform,
      encoder = self.ffencoder,
      profile = self.profile,
      context = [f"key:model/encode/{codec}", "base.origin"],
    )

    for gop in [1, 30]:
      get_media()._set_test_details(gop = gop)
      vars(self).update(gop = gop)

      self.xdata = list()
      self.ydata = list()

      for qp in self.modelqps:
        get_media()._set_test_details(qp = qp)
        vars(self).update(qp = qp)
        self.encode()

      label = f"{platform}:{codec}:{self.rcmode}:{self.case}:gop={gop}"

      plt.ylabel("PSNR")
      plt.xlabel("Compression Ratio (ln x)")

      plt.scatter(self.xdata, self.ydata, label = label)


      best_model = [0, None, None]
      for fn in self.modelfns:
        try:
          popt, pcov = curve_fit(trend_models[fn], self.xdata, self.ydata)
        except:
          continue

        ydata = np.array(self.ydata)
        xdata = np.array(self.xdata)

        # calculate R-squared
        residuals = ydata - trend_models[fn](xdata, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((ydata - np.mean(ydata))**2)
        rsq = 1 - (ss_res / ss_tot)

        if rsq < 0.9: continue # not a very good fit

        if rsq > best_model[0]:
          best_model = [rsq, fn, popt]

      rsq, fn, popt = best_model

      get_media().baseline.update_reference(
        fx = fn, popt = list(popt), rsq = rsq,
        context = [f"key:model/encode/{codec}", f"gop.{gop}"],
      )

      power_x = np.linspace(min(self.xdata + [0]), max(self.xdata + [10]), 100)
      power_y = trend_models[fn](power_x, *popt)
      power_y = [max(20, p - tolerance) for p in power_y]
      sopt = tuple(float(f"{p:.2f}") for p in popt)

      plt.plot(
        power_x, power_y,
        label = f"{label}.{fn}{sopt}(r2={rsq:.4f}, T={tolerance})"
      )

    plt.ylim([15, 100])
    plt.legend()
    plt.savefig(get_media().artifacts.reserve("svg"))
    # plt.show()
    plt.clf()

  def check_metrics(self):
    self.decoder.update(source = self.encoder.encoded, metric = self.metric)
    self.decoder.decode()

    metric = metrics2.factory.create(**vars(self))
    metric.update(
      filecoded = self.encoder.encoded,
      filetrue  = self.source,
      filetest  = self.decoder.decoded,
    )
    metric.actual = self.parse_psnr()
    get_media()._set_test_details(**{
      "compression:ratio" : metric.compratio,
      "compression:log"   : metric.logratio,
      "psnr:stats"        : metric.actual,
      "psnr"              : metric.average,
    })
    self.xdata.append(metric.logratio)
    self.ydata.append(metric.average)
