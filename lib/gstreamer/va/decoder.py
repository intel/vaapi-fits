###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ....lib import platform
from ....lib.codecs import Codec
from ....lib.common import get_media
from ....lib.formats import PixelFormat
from ....lib.gstreamer.decoderbase import BaseDecoderTest, Decoder as GstDecoder
from ....lib.gstreamer.util import have_gst_element
from ....lib.gstreamer.va.util import mapformat, mapformatu

class Decoder(GstDecoder):
  format  = property(lambda s: mapformatu(super().format))
  pformat = property(lambda s: mapformat(super().format))

@slash.requires(*have_gst_element("va"))
class DecoderTest(BaseDecoderTest):
  DecoderClass = Decoder

  def before(self):
    super().before()

def decode_test_class(codec, bitdepth, **kwargs):
  # caps lookup translation
  capcodec = codec
  if codec in [Codec.HEVC, Codec.VP9, Codec.AV1, Codec.VVC]:
    capcodec = f"{codec}_{bitdepth}"

  # gst element codec translation
  gstcodec = {
    Codec.AVC   : "h264",
    Codec.HEVC  : "h265",
    Codec.VVC   : "h266",
  }.get(codec, codec)

  gstparser = {
    Codec.MPEG2 : "mpegvideoparse",
    Codec.VP8   : None,
  }.get(codec, f"{gstcodec}parse")

  hwdevice = get_media().render_device.split('/')[-1]
  hw = hwdevice if hwdevice not in ['renderD128', '0'] else ""

  @slash.requires(*have_gst_element(f"va{hw}{gstcodec}dec"))
  @slash.requires(*platform.have_caps("decode", capcodec))
  class CodecDecoderTest(DecoderTest):
    def before(self):
      super().before()
      vars(self).update(
        caps = platform.get_caps("decode", capcodec),
        codec = codec,
        gstdecoder = f"va{hw}{gstcodec}dec",
        gstparser = gstparser,
        **kwargs,
      )

    def validate_caps(self):
      assert PixelFormat(self.format).bitdepth == bitdepth
      super().validate_caps()

  return CodecDecoderTest

## AVC ##
AVCDecoderTest      = decode_test_class(codec = Codec.AVC, bitdepth = 8)

## HEVC ##
HEVC_8DecoderTest   = decode_test_class(codec = Codec.HEVC, bitdepth = 8)
HEVC_10DecoderTest  = decode_test_class(codec = Codec.HEVC, bitdepth = 10)
HEVC_12DecoderTest  = decode_test_class(codec = Codec.HEVC, bitdepth = 12)

## AV1 ##
AV1_8DecoderTest    = decode_test_class(codec = Codec.AV1, bitdepth = 8)
AV1_10DecoderTest   = decode_test_class(codec = Codec.AV1, bitdepth = 10)

## VP9 ##
VP9_8DecoderTest    = decode_test_class(codec = Codec.VP9, bitdepth = 8)
VP9_10DecoderTest   = decode_test_class(codec = Codec.VP9, bitdepth = 10)
VP9_12DecoderTest   = decode_test_class(codec = Codec.VP9, bitdepth = 12)

## VP8 ##
VP8DecoderTest      = decode_test_class(codec = Codec.VP8, bitdepth = 8)

## JPEG/MJPEG ##
JPEGDecoderTest     = decode_test_class(codec = Codec.JPEG, bitdepth = 8)

## MPEG2 ##
MPEG2DecoderTest    = decode_test_class(codec = Codec.MPEG2, bitdepth = 8)

## VVC ##
VVC_8DecoderTest    = decode_test_class(codec = Codec.VVC, bitdepth = 8)
VVC_10DecoderTest   = decode_test_class(codec = Codec.VVC, bitdepth = 10)
