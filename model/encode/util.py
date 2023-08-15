###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ...lib import *
from ...lib import metrics2
from ...lib.metrics2.psnr import trend_models

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
      slices  = 1,
      quality = 4,
    )
    vars(self).setdefault("profile", default_profile)

  def fit(self):
    self.initvars("main")

    platform = get_media()._get_platform_name()
    tolerance = vars(self).get("metric", dict()).get("tolerance", 5.0)
    qps = [1, 2, 4, 7, 10, 13, 16, 23, 31, 40, 42, 45, 48, 49, 51]

    for gop, bf, tu in itertools.product([1, 30], [2], [4]):
      get_media()._set_test_details(gop = gop, bframes = bf, tu = tu)
      vars(self).update(gop = gop, bframes = bf, quality = tu)

      self.xdata = list()
      self.ydata = list()

      for qp in qps:
        get_media()._set_test_details(qp = qp)
        vars(self).update(qp = qp)
        self.encode()

      label = f"{platform}:{self.codec}:{self.rcmode}:{self.case}:gop={gop}:bf={bf}:tu={tu}"

      plt.ylabel("PSNR")
      plt.xlabel("Compression Ratio (ln x)")

      plt.scatter(self.xdata, self.ydata, label = label)

      for fn in ["powernc", "powerc", "powern", "power"]:
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

        get_media().baseline.update_reference(
          fx = fn, popt = list(popt), rsq = rsq,
          context = [f"key:model/encode/{self.codec}", f"gop.{gop}"],
        )

        power_x = np.linspace(min(self.xdata), max(self.xdata), 100)
        power_y = trend_models[fn](power_x, *popt)
        power_y = [max(20, p - tolerance) for p in power_y]
        sopt = tuple(float(f"{p:.2f}") for p in popt)

        plt.plot(
          power_x, power_y,
          label = f"{label}.{fn}{sopt}(r2={rsq:.4f}, T={tolerance})"
        )

        break # only need one trend model function

    plt.ylim([15, 100])
    plt.legend()
    plt.savefig(get_media()._test_artifact2("svg"))
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
    get_media()._set_test_details(psnr = metric.actual, apsnr = metric.average)
    self.xdata.append(metric.logratio)
    self.ydata.append(metric.average)
