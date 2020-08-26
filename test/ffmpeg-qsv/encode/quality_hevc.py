###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ..util import *
from .quality_encoder import EncoderQualityTest

spec      = load_test_spec("hevc", "quality", "8bit")

class HEVC8EncoderQualityTest(EncoderQualityTest):
  def before(self):
    vars(self).update(
      codec     = "hevc-8",
      ffencoder = "hevc_qsv",
      lowpower  = 0,
    )
    super(HEVC8EncoderQualityTest, self).before()

  def get_file_ext(self):
    return "h265"

class vbr(HEVC8EncoderQualityTest):
  def init(self, tspec, case, gop, bframes, fps, quality, refs, profile):
    self.caps = platform.get_caps("encode", "hevc_8")
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
      case    = case,
      fps     = fps,
      gop     = gop,
      profile = profile,
      quality = quality,
      rcmode  = "vbr",
      refs    = refs,
    )

  @slash.requires(*platform.have_caps("encode", "hevc_8"))
  @slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
  @slash.parametrize(*gen_hevc_vbr_quality_parameters(spec, ['main']))
  def test(self, case, gop, bframes, fps, quality, refs, profile):
    bitrate_psnr=[]
    self.init(spec, case, gop, bframes, fps, quality, refs, profile)
    platform=self.get_platform()
    assert vars(self)["platform_map"][platform], "X265 reference value for "+ platform +" is None"
    for i in range(0,4):
        bitrate_psnr.append(self.encode(vars(self)["bitrate"][i],i))
    self.check_metrics([vars(self)["platform_map"][platform]["vbr_refs"][0][0],vars(self)["platform_map"][platform]["vbr_refs"][1][0],vars(self)["platform_map"][platform]["vbr_refs"][2][0],vars(self)["platform_map"][platform]["vbr_refs"][3][0]],
                       [vars(self)["platform_map"][platform]["vbr_refs"][0][1],vars(self)["platform_map"][platform]["vbr_refs"][1][1],vars(self)["platform_map"][platform]["vbr_refs"][2][1],vars(self)["platform_map"][platform]["vbr_refs"][3][1]],
                       [bitrate_psnr[0][0][0],bitrate_psnr[1][0][0],bitrate_psnr[2][0][0],bitrate_psnr[3][0][0]],
                       [bitrate_psnr[0][0][1],bitrate_psnr[1][0][1],bitrate_psnr[2][0][1],bitrate_psnr[3][0][1]])
