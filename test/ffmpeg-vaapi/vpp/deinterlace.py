###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

if len(load_test_spec("vpp", "deinterlace")):
  slash.logger.warn(
    "ffmpeg-vaapi: vpp deinterlace with raw input is no longer supported")

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_vaapi_accel)
@slash.requires(*have_ffmpeg_filter("deinterlace_vaapi"))
class DeinterlaceTest(slash.Test):
  _default_methods_ = [
    "bob",
    "weave",
    "motion-adaptive",
    "motion-compensated"
  ]

  _default_modes_ = [
    dict(zip(["method", "rate"], m)) for m in itertools.product(
        _default_methods_, ["field", "frame"])]

  def before(self):
    # default metric
    self.metric = dict(type = "md5")
    self.refctx = []

  @timefn("ffmpeg")
  def call_ffmpeg(self):
    call(
      "ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 -v verbose"
      " -c:v {ffdecoder} -i {source} -vf 'format=nv12|vaapi,hwupload,"
      "deinterlace_vaapi=mode={mmethod}:rate={rate},hwdownload,format=nv12'"
      " -pix_fmt {mformat} -f rawvideo -vsync passthrough -an -vframes {frames}"
      " -y {decoded}".format(**vars(self)))

  def get_name_tmpl(self):
    return "{case}_di_{method}_{rate}_{width}x{height}_{format}"

  def deinterlace(self):
    self.mformat = mapformat(self.format)
    self.mmethod = map_deinterlace_method(self.method)

    if self.mformat is None:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    if self.mmethod is None:
      slash.skip_test("{method} method not supported".format(**vars(self)))

    name = self.get_name_tmpl().format(**vars(self))
    self.decoded = get_media()._test_artifact("{}.yuv".format(name))
    # field rate produces double number of frames.
    self.frames *= 2 if "field" == self.rate else 1
    self.call_ffmpeg()
    self.check_metrics()

  def check_metrics(self):
    check_filesize(
      self.decoded, self.width, self.height, self.frames, self.format)
    if vars(self).get("reference", None) is not None:
      self.reference = format_value(self.reference, **vars(self))
    check_metric(**vars(self))

spec_avc = load_test_spec("vpp", "deinterlace", "avc")
class avc(DeinterlaceTest):
  def before(self):
    self.ffdecoder = "h264"
    super(avc, self).before()

  @platform_tags(set(AVC_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_ffmpeg_decoder("h264"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_avc, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    vars(self).update(spec_avc[case].copy())
    vars(self).update(case = case, method = method, rate = rate)
    self.deinterlace()

spec_mpeg2 = load_test_spec("vpp", "deinterlace", "mpeg2")
class mpeg2(DeinterlaceTest):
  def before(self):
    self.ffdecoder = "mpeg2video"
    super(mpeg2, self).before()

  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_ffmpeg_decoder("mpeg2video"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_mpeg2, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    vars(self).update(spec_mpeg2[case].copy())
    vars(self).update(case = case, method = method, rate = rate)
    self.deinterlace()

spec_vc1 = load_test_spec("vpp", "deinterlace", "vc1")
class vc1(DeinterlaceTest):
  def before(self):
    self.ffdecoder = "vc1"
    super(vc1, self).before()

  @platform_tags(set(VC1_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_ffmpeg_decoder("vc1"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_vc1, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    vars(self).update(spec_vc1[case].copy())
    vars(self).update(case = case, method = method, rate = rate)
    self.deinterlace()
