###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *

if len(load_test_spec("vpp", "deinterlace")):
  slash.logger.warn(
    "ffmpeg-qsv: vpp deinterlace with raw input is no longer supported")

@slash.requires(have_ffmpeg)
@slash.requires(have_ffmpeg_qsv_accel)
@slash.requires(*have_ffmpeg_filter("vpp_qsv"))
@slash.requires(using_compatible_driver)
class DeinterlaceTest(slash.Test):
  _default_methods_ = [
    "bob",
    "advanced",
  ]

  _default_modes_ = [
    dict(method = m, rate = "frame") for m in _default_methods_
  ]

  def before(self):
    # default metric
    self.metric = dict(type = "md5")
    self.refctx = []

  @timefn("ffmpeg")
  def call_ffmpeg(self):
    call(
      "ffmpeg -init_hw_device qsv=qsv:hw -hwaccel qsv -filter_hw_device qsv"
      " -v verbose -c:v {ffdecoder} -i {source}"
      " -vf 'format=nv12|qsv,hwupload=extra_hw_frames=16"
      ",vpp_qsv=deinterlace={method},hwdownload,format=nv12'"
      " -pix_fmt {mformat} -f rawvideo -vsync passthrough -an -vframes {frames}"
      " -y {decoded}".format(**vars(self)))

  def get_name_tmpl(self):
    return "{case}_di_{method}_{rate}_{width}x{height}_{format}"

  def deinterlace(self):
    self.mformat = mapformat(self.format)
    self.mmethod = map_deinterlace_method(self.method)

    # The rate is fixed in vpp_qsv deinterlace.  It always outputs at frame
    # rate (one frame of output for each field-pair).
    if "frame" != self.rate:
      slash.skip_test("{rate} rate not supported".format(**vars(self)))

    if self.mformat is None:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    if self.mmethod is None:
      slash.skip_test("{method} method not supported".format(**vars(self)))

    name = self.get_name_tmpl().format(**vars(self))
    self.decoded = get_media()._test_artifact("{}.yuv".format(name))
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
    self.ffdecoder = "h264_qsv"
    super(avc, self).before()

  @platform_tags(set(AVC_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_ffmpeg_decoder("h264_qsv"))
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
    self.ffdecoder = "mpeg2_qsv"
    super(mpeg2, self).before()

  @platform_tags(set(MPEG2_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_ffmpeg_decoder("mpeg2_qsv"))
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
    self.ffdecoder = "vc1_qsv"
    super(vc1, self).before()

  @platform_tags(set(VC1_DECODE_PLATFORMS) & set(VPP_PLATFORMS))
  @slash.requires(*have_ffmpeg_decoder("vc1_qsv"))
  @slash.parametrize(
    *gen_vpp_deinterlace_parameters(
      spec_vc1, DeinterlaceTest._default_modes_))
  def test(self, case, method, rate):
    vars(self).update(spec_vc1[case].copy())
    vars(self).update(case = case, method = method, rate = rate)
    self.deinterlace()
