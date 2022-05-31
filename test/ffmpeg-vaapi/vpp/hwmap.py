###
### Copyright (C) 2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.vpp import VppTest

spec      = load_test_spec("vpp", "vaapi_hwmap")

@slash.requires(*platform.have_caps("vpp", "scale"))
@slash.requires(*have_ffmpeg_filter("scale_qsv"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "scale"),
    )
    super(default, self).before()

  def init(self, tspec, case, scale_width, scale_height, vpp_op, encoder):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case          = case,
      scale_height  = scale_height,
      scale_width   = scale_width,
      vpp_op        = vpp_op,
      encoder       = encoder,
    )

  @slash.parametrize(*gen_vpp_hwmap_parameters(spec))
  def test(self, case, scale_width, scale_height, vpp_op, encoder):
    self.init(spec, case, scale_width, scale_height, vpp_op, encoder)
    self.vpp()

  def check_psnr(self):
    iopts = "-hwaccel_output_format vaapi "
    if vars(self).get("ffdecoder", None) is not None:
      iopts += "-c:v {ffdecoder} "
    iopts += "-i {encoded}"

    fmtref = format_value(self.reference, **vars(self))
    name = (self.gen_name() + "-{width}x{height}-{format}").format(**vars(self))
    self.decode = get_media()._test_artifact("{}.yuv".format(name))
    oopts = (
      "-vf 'hwdownload,format={ohwformat}' -pix_fmt {mformat} -f rawvideo"
      " -vsync passthrough -vframes {frames}"
      f" -y {filepath2os(self.decode)}")
    self.call_ffmpeg(iopts.format(**vars(self)), oopts.format(**vars(self)))
    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        fmtref, self.decode,
        self.scale_width, self.scale_height,
        self.frames, self.format),
      context = self.refctx,
    )

  def check_ssim(self):
    check_filesize(
        self.decoded, self.scale_width, self.scale_height,
        self.frames, self.format)

    fmtref = format_value(self.reference, **vars(self))

    ssim = calculate_ssim(
      fmtref, self.decoded,
      self.scale_width, self.scale_height,
      self.frames, self.format)

    get_media()._set_test_details(ssim = ssim)

    assert 1.0 >= ssim[0] >= 0.97
    assert 1.0 >= ssim[1] >= 0.97
    assert 1.0 >= ssim[2] >= 0.97

  def check_metrics(self):
    if vars(self).get("encoder", None) is None:
      self.check_ssim()
    else:
      self.check_psnr()

     
        
