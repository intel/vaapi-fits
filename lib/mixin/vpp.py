###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .. import metrics2
from ..common import get_media
from ..util import format_value

class VppMetricMixin:
  def compare_brightness(self, k, ref, actual):
    assert ref is not None, "Invalid reference value"
    assert abs(ref[-3] - actual[-3]) < 0.2, "Luma (Y) out of baseline range"
    assert actual[-2] == 100, "Cb(U) should not be affected by BRIGHTNESS filter"
    assert actual[-1] == 100, "Cr(V) should not be affected by BRIGHTNESS filter"

  def compare_contrast(self, k, ref, actual):
    assert ref is not None, "Invalid reference value"
    assert abs(ref[-3] - actual[-3]) < 0.2, "Luma (Y) out of baseline range"
    assert abs(ref[-2] - actual[-2]) < 0.2, "Cb (U) out of baseline range"
    assert abs(ref[-1] - actual[-1]) < 0.2, "Cr (V) out of baseline range"

  def compare_hue(self, k, ref, actual):
    assert ref is not None, "Invalid reference value"
    assert actual[-3] == 100, "Luma (Y) should not be affected by HUE filter"
    assert abs(ref[-2] - actual[-2]) < 0.2, "Cb (U) out of baseline range"
    assert abs(ref[-1] - actual[-1]) < 0.2, "Cr (V) out of baseline range"

  def compare_saturation(self, k, ref, actual):
    assert ref is not None, "Invalid reference value"
    assert actual[-3] == 100, "Luma (Y) should not be affected by SATURATION filter"
    assert abs(ref[-2] - actual[-2]) < 0.2, "Cb (U) out of baseline range"
    assert abs(ref[-1] - actual[-1]) < 0.2, "Cr (V) out of baseline range"

  def check_procamp(self):
    if 50 == self.level: # NOOP (default level)
      metric = metrics2.factory.create(
        metric = dict(type = "md5"),
        width = self.width, height = self.height,
        frames = self.frames, format = self.format)
      metric.update(filetest = self.source)
      metric.expect = metric.actual
      metric.update(filetest = self.decoded)
      metric.check()
    else:
      metrics2.check(
        metric = dict(type = "psnr"),
        compare = getattr(self, "compare_{vpp_op}".format(**vars(self))),
        filetrue = self.source, filetest = self.decoded,
        width = self.width, height = self.height, frames = self.frames,
        format = self.format, refctx = self.refctx)

  check_brightness  = check_procamp
  check_contrast    = check_procamp
  check_hue         = check_procamp
  check_saturation  = check_procamp

  def check_crop(self):
    metrics2.check(
      metric = dict(type = "filesize"), filetest = self.decoded,
      width = self.crop_width, height = self.crop_height,
      frames = self.frames, format = self.format)

    params = vars(self).copy()
    params.update(width = self.crop_width, height = self.crop_height)

    metrics2.check(**params)

  def check_csc(self):
    metrics2.check(
      # if user specified metric, then use it.  Otherwise, use ssim metric with perfect score
      metric = vars(self).get("metric", dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)),
      # If user specified reference, use it.  Otherwise, assume source is the reference.
      filetrue = format_value(self.reference, **vars(self))
        if vars(self).get("reference") else self.source,
      filetest = self.decoded,
      # if user specified reference, then assume it's format is the same as csc output format.
      # Otherwise, the format is the source format
      format = self.format if vars(self).get("reference", None) is None else self.csc,
      format2 = self.csc,
      width = self.width, height = self.height, frames = self.frames)

  def check_deinterlace(self):
    if vars(self).get("reference", None) is not None:
      self.reference = format_value(self.reference, **vars(self))
    metrics2.check(**vars(self))

  def check_denoise(self):
    def compare(k, ref, actual):
      assert ref is not None, "Invalid reference value"
      assert abs(ref[-3] - actual[-3]) < 0.2, "Luma (Y) out of baseline range"
      if self.caps.get("chroma", True):
        assert abs(ref[-2] - actual[-2]) < 0.2, "Cb (U) out of baseline range"
        assert abs(ref[-1] - actual[-1]) < 0.2, "Cr (V) out of baseline range"
      else:
        assert actual[-2] == 100, "Cb(U) changed, but caps don't support DENOISE chroma"
        assert actual[-1] == 100, "Cr(V) changed, but caps don't support DENOISE chroma"

    metrics2.check(
      metric = dict(type = "psnr"), compare = compare,
      filetrue = self.source, filetest = self.decoded,
      width = self.width, height = self.height, frames = self.frames,
      format = self.format, refctx = self.refctx)

  def check_scale(self):
    metrics2.check(
      metric = dict(type = "filesize"),
      filetest = self.decoded, width = self.scale_width,
      height = self.scale_height, frames = self.frames, format = self.format)
    metrics2.check(
      metric = dict(type = "ssim", miny = 0.97, minu = 0.97, minv = 0.97),
      filetrue = format_value(self.reference, **vars(self)),
      filetest = self.decoded, width = self.scale_width,
      height = self.scale_height, frames = self.frames, format = self.format)

  # FIXME: HACK: "generic" class should not have concept of "qsv"
  check_scale_qsv = check_scale

  def check_sharpen(self):
    def compare(k, ref, actual):
      assert actual[-2] == 100, "Cb(U) should not be affected by SHARPEN filter"
      assert actual[-1] == 100, "Cr(V) should not be affected by SHARPEN filter"
      assert ref is not None, "Invalid reference value"
      assert abs(ref[-3] - actual[-3]) <  0.25, "Luma (Y) out of baseline range"

    metrics2.check(
      metric = dict(type = "psnr"), compare = compare,
      filetrue = self.source, filetest = self.decoded,
      width = self.width, height = self.height, frames = self.frames,
      format = self.format, refctx = self.refctx)

  def check_composite(self):
    owidth, oheight = self.width, self.height
    for comp in self.comps:
      owidth = max(owidth, self.width + comp['x'])
      oheight = max(oheight, self.height + comp['y'])

    metrics2.check(
      metric = dict(type = "filesize"),
      filetest = self.decoded, width = owidth, height = oheight,
      frames = self.frames, format = self.format)

    params = vars(self).copy()
    params.update(width = owidth, height = oheight)

    metrics2.check(**params)

  def check_default(self):
    metrics2.check(**vars(self))

  def check_metrics(self):
    getattr(self, "check_{vpp_op}".format(**vars(self)), self.check_default)()
