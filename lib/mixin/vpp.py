###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .. import metrics
from ..common import get_media
from ..util import format_value

class VppMetricMixin:

  def compare_brightness(self, k, ref, actual):
    assert ref is not None, "Invalid reference value"
    assert abs(ref[-3] - actual[-3]) <  0.2, "Luma (Y) out of baseline range"
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
    assert abs(ref[-2] - actual[-2]) <  0.2, "Cb (U) out of baseline range"
    assert abs(ref[-1] - actual[-1]) <  0.2, "Cr (V) out of baseline range"

  def compare_saturation(self, k, ref, actual):
    assert ref is not None, "Invalid reference value"
    assert actual[-3] == 100, "Luma (Y) should not be affected by SATURATION filter"
    assert abs(ref[-2] - actual[-2]) <  0.2, "Cb (U) out of baseline range"
    assert abs(ref[-1] - actual[-1]) <  0.2, "Cr (V) out of baseline range"

  def check_procamp(self):
    psnr = metrics.calculate_psnr(
      self.source, self.decoded,
      self.width, self.height,
      self.frames, self.format)

    if 50 == self.level: # NOOP (default level)
      get_media()._set_test_details(psnr = psnr, ref_psnr = "noop")
      assert psnr[-3] == 100, "Luma (Y) should not be affected at NOOP level"
      assert psnr[-2] == 100, "Cb (U) should not be affected at NOOP level"
      assert psnr[-1] == 100, "Cr (V) should not be affected at NOOP level"
    else:
      compare = getattr(self, "compare_{vpp_op}".format(**vars(self)))
      get_media().baseline.check_result(
        compare = compare, context = self.refctx, psnr = psnr)

  check_brightness  = check_procamp
  check_contrast    = check_procamp
  check_hue         = check_procamp
  check_saturation  = check_procamp

  def check_crop(self):
    metrics.check_filesize(
      self.decoded, self.crop_width, self.crop_height, self.frames, self.format)

    params = vars(self).copy()
    params["width"] = self.crop_width
    params["height"] = self.crop_height

    metrics.check_metric(**params)

  def check_csc(self):
    metrics.check_metric(
      # if user specified metric, then use it.  Otherwise, use ssim metric with perfect score
      metric = vars(self).get("metric", dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)),
      # If user specified reference, use it.  Otherwise, assume source is the reference.
      reference = format_value(self.reference, **vars(self))
        if vars(self).get("reference") else self.source,
      decoded = self.decoded,
      # if user specified reference, then assume it's format is the same as csc output format.
      # Otherwise, the format is the source format
      format = self.format if vars(self).get("reference", None) is None else self.csc,
      format2 = self.csc,
      width = self.width, height = self.height, frames = self.frames)

  def check_deinterlace(self):
    if vars(self).get("reference", None) is not None:
      self.reference = format_value(self.reference, **vars(self))
    metrics.check_metric(**vars(self))

  def check_denoise(self):
    psnr = metrics.calculate_psnr(
      self.source, self.decoded,
      self.width, self.height,
      self.frames, self.format)

    def compare(k, ref, actual):
      assert ref is not None, "Invalid reference value"
      assert abs(ref[-3] - actual[-3]) < 0.2, "Luma (Y) out of baseline range"
      if self.caps.get("chroma", True):
        assert abs(ref[-2] - actual[-2]) < 0.2, "Cb (U) out of baseline range"
        assert abs(ref[-1] - actual[-1]) < 0.2, "Cr (V) out of baseline range"
      else:
        assert actual[-2] == 100, "Cb(U) changed, but caps don't support DENOISE chroma"
        assert actual[-1] == 100, "Cr(V) changed, but caps don't support DENOISE chroma"

    get_media().baseline.check_result(
      compare = compare, context = self.refctx, psnr = psnr)

  def check_scale(self):
    metrics.check_filesize(
      self.decoded, self.scale_width, self.scale_height,
      self.frames, self.format)

    fmtref = format_value(self.reference, **vars(self))

    ssim = metrics.calculate_ssim(
      fmtref, self.decoded,
      self.scale_width, self.scale_height,
      self.frames, self.format)

    get_media()._set_test_details(ssim = ssim)

    assert 1.0 >= ssim[0] >= 0.97
    assert 1.0 >= ssim[1] >= 0.97
    assert 1.0 >= ssim[2] >= 0.97

  def check_sharpen(self):
    psnr = metrics.calculate_psnr(
      self.source, self.decoded,
      self.width, self.height,
      self.frames, self.format)

    assert psnr[-2] == 100, "Cb(U) should not be affected by SHARPEN filter"
    assert psnr[-1] == 100, "Cr(V) should not be affected by SHARPEN filter"

    def compare(k, ref, actual):
      assert ref is not None, "Invalid reference value"
      assert abs(ref[-3] - actual[-3]) <  0.25, "Luma (Y) out of baseline range"

    get_media().baseline.check_result(
      compare = compare, context = self.refctx, psnr = psnr)

  def check_composite(self):
    owidth, oheight = self.width, self.height
    for comp in self.comps:
      owidth = max(owidth, self.width + comp['x'])
      oheight = max(oheight, self.height + comp['y'])

    params = vars(self).copy()
    params["width"] = owidth
    params["height"] = oheight

    metrics.check_filesize(self.decoded, owidth, oheight, self.frames, self.format)
    metrics.check_metric(**params)

  def check_default(self):
    metrics.check_metric(**vars(self))

  def check_metrics(self):
    getattr(self, "check_{vpp_op}".format(**vars(self)), self.check_default)()
