###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import re
import slash

from ....lib import platform
from ....lib.ffmpeg.encoderbase import BaseEncoderTest, Encoder as FFEncoder
from ....lib.ffmpeg.util import have_ffmpeg_hwaccel, have_ffmpeg_encoder, have_ffmpeg_decoder
from ....lib.ffmpeg.qsv.util import mapprofile, using_compatible_driver, have_encode_main10sp
from ....lib.ffmpeg.qsv.decoder import Decoder
from ....lib.common import mapRangeInt, get_media, call, exe2os
from ....lib.codecs import Codec

class Encoder(FFEncoder):
  hwaccel   = property(lambda s: "qsv")
  tilecols  = property(lambda s: s.ifprop("tilecols", " -tile_cols {tilecols}"))
  tilerows  = property(lambda s: s.ifprop("tilerows", " -tile_rows {tilerows}"))
  ldb       = property(lambda s: s.ifprop("ldb", " -low_delay_brc {ldb}"))
  iqfactor  = property(lambda s: s.ifprop("iqfactor", " -i_qfactor {iqfactor}"))
  bqfactor  = property(lambda s: s.ifprop("bqfactor", " -b_qfactor {bqfactor}"))
  iqoffset  = property(lambda s: s.ifprop("iqoffset", " -i_qoffset {iqoffset}"))
  bqoffset  = property(lambda s: s.ifprop("bqoffset", " -b_qoffset {bqoffset}"))

  @property
  def hwupload(self):
    return f"{super().hwupload}=extra_hw_frames=120"

  @property
  def hwdevice(self):
    return f'qsv,child_device={get_media().render_device}'

  @property
  def qp(self):
    def inner(qp):
      if self.codec in [Codec.MPEG2]:
        mqp = mapRangeInt(qp, [0, 100], [1, 51])
        return f" -q {mqp}"
      return f" -q {qp}"
    return self.ifprop("qp", inner)

  @property
  def quality(self):
    def inner(quality):
      if self.codec in [Codec.JPEG]:
        return f" -global_quality {quality}"
      return f" -preset {quality}"
    return self.ifprop("quality", inner)

  @property
  def encparams(self):
    return (
      f"{super().encparams}{self.ldb}"
      f"{self.iqfactor}{self.bqfactor}"
      f"{self.iqoffset}{self.bqoffset}"
    )

@slash.requires(*have_ffmpeg_hwaccel("qsv"))
@slash.requires(using_compatible_driver)
class EncoderTest(BaseEncoderTest):
  EncoderClass = Encoder
  DecoderClass = Decoder

  def map_profile(self):
    return mapprofile(self.codec, self.profile)

  def validate_caps(self):
    if vars(self).get("profile", None) in ["main10sp"] and not have_encode_main10sp(self.ffencoder):
      slash.skip_test(f"{self.ffencoder} main10sp not supported")

    # FIXME: this should go into BaseEncoderTest
    if self.rcmode in ["cbr", "vbr"]:
      # brframes, if specified, overrides "frames" for bitrate control modes
      self.frames = vars(self).get("brframes", self.frames)

    super().validate_caps()

  def check_metrics(self):
    # TCBRC check
    is_tcbrc = all([
      self.rcmode in ["vbr"],
      vars(self).get("lowpower", 0),
      vars(self).get("ldb", 0),
      vars(self).get("strict", 0) == -1,
    ])

    if is_tcbrc:
      output = call(
        f"{exe2os('ffprobe')} -i {self.encoder.osencoded}"
        f" -show_entries frame=pkt_size,pict_type -of compact"
      )

      actual = re.findall(r'(?<=pkt_size=).[0-9]*(?=\|pict_type=[IPB])', output)
      assert len(actual) == self.frames, "Probe failed for frame pkt_size"

      target = self.bitrate * 1000 / 8 / self.fps # target bytes per frame
      results = [int(frmsize) < target * 1.2 for frmsize in actual]
      failed = results.count(False)
      rate = failed / len(results)

      get_media()._set_test_details(**{
        "tcbrc:frame:target (bytes)" : f"{target:0.2f}",
        "tcbrc:frame:fails" : f"{failed} ({rate:0.2%})",
      })

      assert rate < 0.2, "Too many TCBRC frames exceed target frame size"

    super().check_metrics()

  def check_output(self):
    # init
    m = re.search("Initialize MFX session", self.output, re.MULTILINE)
    assert m is not None, "It appears that the QSV plugin did not load"

    # rate control mode
    if self.codec not in [Codec.JPEG]:
      mode = "LA" if vars(self).get("ladepth", None) is not None else self.rcmode
      m = re.search(f"RateControlMethod: {mode.upper()}", self.output, re.MULTILINE)
      assert m is not None, "Possible incorrect RC mode used"

    # lowpower
    if self.codec not in [Codec.JPEG, Codec.MPEG2]:
      if get_media()._get_gpu_gen() < 13:
         vdenc = "ON" if vars(self).get("lowpower", 0) else "OFF"
      else:
         vdenc = "OFF" if vars(self).get("lowpower", 0) else "ON"
      m = re.search(f"VDENC: {vdenc}", self.output, re.MULTILINE)
      assert m is not None, "Possible incorrect VDENC/VME mode used"

    # fps
    if vars(self).get("fps", None) is not None:
      m = re.search(f"FrameRateExtD: 1; FrameRateExtN: {self.fps}", self.output, re.MULTILINE)
      assert m is not None, "Possible incorrect FPS used"

    # slices
    if vars(self).get("slices", None) is not None and self.codec not in [Codec.VP9]:
      m = re.search(f"NumSlice: {self.slices};", self.output, re.MULTILINE)
      assert m is not None, "Possible incorrect slices used"

    # ladepth
    if vars(self).get("ladepth", None) is not None:
      m = re.search(f"LookAheadDepth: {self.ladepth}", self.output, re.MULTILINE)
      assert m is not None, "The lookahead depth does not match test parameter"

    # main10sp
    if vars(self).get("profile", None) in ["main10sp"]:
      m = re.search(r"Main10sp.*: enable", self.output, re.MULTILINE)
      assert m is not None, "It appears that main10sp did not get enabled"

    # intref
    if vars(self).get("intref", None) is not None:
      patterns = [
        f"IntRefType: {self.intref['type']};",
        f"IntRefCycleSize: {self.intref['size']};",
        f"IntRefCycleDist: {self.intref['dist']}",
      ]

      for pattern in patterns:
        m = re.search(pattern, self.output, re.MULTILINE)
        assert m is not None, f"'{pattern}' missing in output"

    # Max/min qp
    if vars(self).get("rqp", None) is not None:
      patterns = [
        f"MinQPI: {self.rqp['MinQPI']};",
        f"MaxQPI: {self.rqp['MaxQPI']};",
        f"MinQPP: {self.rqp['MinQPP']};",
        f"MaxQPP: {self.rqp['MaxQPP']};",
        f"MinQPB: {self.rqp['MinQPB']};",
        f"MaxQPB: {self.rqp['MaxQPB']}",
      ]

      for pattern in patterns:
        m = re.search(pattern, self.output, re.MULTILINE)
        assert m is not None, f"'{pattern}' missing in output"

############################
## AVC Encoders           ##
############################

@slash.requires(*have_ffmpeg_encoder("h264_qsv"))
@slash.requires(*have_ffmpeg_decoder("h264_qsv"))
class AVCEncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec     = Codec.AVC,
      ffencoder = "h264_qsv",
      ffdecoder = "h264_qsv",
    )

  def get_file_ext(self):
    return "h264"

@slash.requires(*platform.have_caps("encode", "avc"))
class AVCEncoderTest(AVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "avc"),
      lowpower  = 0,
    )

@slash.requires(*platform.have_caps("vdenc", "avc"))
class AVCEncoderLPTest(AVCEncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "avc"),
      lowpower  = 1,
    )

############################
## HEVC 8 Bit Encoders    ##
############################

@slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
@slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
class HEVC8EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec     = Codec.HEVC,
      ffencoder = "hevc_qsv",
      ffdecoder = "hevc_qsv",
    )

  def get_file_ext(self):
    return "h265"

@slash.requires(*platform.have_caps("encode", "hevc_8"))
class HEVC8EncoderTest(HEVC8EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_8"),
      lowpower  = 0,
    )

@slash.requires(*platform.have_caps("vdenc", "hevc_8"))
class HEVC8EncoderLPTest(HEVC8EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "hevc_8"),
      lowpower  = 1,
    )

############################
## HEVC 10 Bit Encoders   ##
############################

@slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
@slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
class HEVC10EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec     = Codec.HEVC,
      ffencoder = "hevc_qsv",
      ffdecoder = "hevc_qsv",
    )

  def get_file_ext(self):
    return "h265"

@slash.requires(*platform.have_caps("encode", "hevc_10"))
class HEVC10EncoderTest(HEVC10EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_10"),
      lowpower  = 0,
    )

@slash.requires(*platform.have_caps("vdenc", "hevc_10"))
class HEVC10EncoderLPTest(HEVC10EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "hevc_10"),
      lowpower  = 1,
    )

############################
## HEVC 12 Bit Encoders   ##
############################

@slash.requires(*have_ffmpeg_encoder("hevc_qsv"))
@slash.requires(*have_ffmpeg_decoder("hevc_qsv"))
class HEVC12EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec     = Codec.HEVC,
      ffencoder = "hevc_qsv",
      ffdecoder = "hevc_qsv",
    )

  def get_file_ext(self):
    return "h265"

@slash.requires(*platform.have_caps("encode", "hevc_12"))
class HEVC12EncoderTest(HEVC12EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_12"),
      lowpower  = 0,
    )

############################
## AV1 8 Bit Encoders     ##
############################

@slash.requires(*have_ffmpeg_encoder("av1_qsv"))
@slash.requires(*have_ffmpeg_decoder("av1_qsv"))
class AV1EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec     = Codec.AV1,
      ffencoder = "av1_qsv",
      ffdecoder = "av1_qsv",
    )

  def get_file_ext(self):
    return "ivf"

@slash.requires(*platform.have_caps("encode", "av1_8"))
class AV1EncoderTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "av1_8"),
      lowpower  = 0,
    )

@slash.requires(*platform.have_caps("vdenc", "av1_8"))
class AV1EncoderLPTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "av1_8"),
      lowpower  = 1,
    )

############################
## AV1 10 Bit Encoders    ##
############################

@slash.requires(*have_ffmpeg_encoder("av1_qsv"))
@slash.requires(*have_ffmpeg_decoder("av1_qsv"))
class AV110EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec     = Codec.AV1,
      ffencoder = "av1_qsv",
      ffdecoder = "av1_qsv",
    )

  def get_file_ext(self):
    return "ivf"

@slash.requires(*platform.have_caps("encode", "av1_10"))
class AV110EncoderTest(AV110EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "av1_10"),
      lowpower  = 0,
    )

@slash.requires(*platform.have_caps("vdenc", "av1_10"))
class AV110EncoderLPTest(AV110EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "av1_10"),
      lowpower  = 1,
    )

############################
## VP9 8 Bit Encoders     ##
############################

@slash.requires(*have_ffmpeg_encoder("vp9_qsv"))
@slash.requires(*have_ffmpeg_decoder("vp9_qsv"))
class VP9_8EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec     = Codec.VP9,
      ffencoder = "vp9_qsv",
      ffdecoder = "vp9_qsv",
    )

  def get_file_ext(self):
    return "ivf"

@slash.requires(*platform.have_caps("encode", "vp9_8"))
class VP9_8EncoderTest(VP9_8EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps = platform.get_caps("encode", "vp9_8"),
      lowpower  = 0,
    )

@slash.requires(*platform.have_caps("vdenc", "vp9_8"))
class VP9_8EncoderLPTest(VP9_8EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "vp9_8"),
      lowpower  = 1,
    )

############################
## MPEG2 Encoders         ##
############################

@slash.requires(*have_ffmpeg_encoder("mpeg2_qsv"))
@slash.requires(*have_ffmpeg_decoder("mpeg2_qsv"))
@slash.requires(*platform.have_caps("encode", "mpeg2"))
class MPEG2EncoderTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "mpeg2"),
      codec     = Codec.MPEG2,
      ffencoder = "mpeg2_qsv",
      ffdecoder = "mpeg2_qsv",
    )

  def get_file_ext(self):
    return "m2v"

############################
## VP9 10 Bit Encoders    ##
############################

@slash.requires(*have_ffmpeg_encoder("vp9_qsv"))
@slash.requires(*have_ffmpeg_decoder("vp9_qsv"))
class VP9_10EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec     = Codec.VP9,
      ffencoder = "vp9_qsv",
      ffdecoder = "vp9_qsv",
    )

  def get_file_ext(self):
    return "ivf"

@slash.requires(*platform.have_caps("encode", "vp9_10"))
class VP9_10EncoderTest(VP9_10EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "vp9_10"),
      lowpower  = 0,
    )

@slash.requires(*platform.have_caps("vdenc", "vp9_10"))
class VP9_10EncoderLPTest(VP9_10EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "vp9_10"),
      lowpower  = 1,
    )
