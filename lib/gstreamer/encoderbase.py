###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash

from ...lib.common import timefn, get_media, call
from ...lib.gstreamer.util import have_gst, have_gst_element
from ...lib.gstreamer.decoderbase import Decoder
from ...lib.metrics import md5, calculate_psnr
from ...lib.parameters import format_value
from ...lib.util import skip_test_if_missing_features
from ...lib.properties import PropertyHandler

class Encoder(PropertyHandler):
  # required properties
  gstencoder    = property(lambda s: s.props["gstencoder"])
  gstmediatype  = property(lambda s: s.props["gstmediatype"])
  codec         = property(lambda s: s.props["codec"])
  rcmode        = property(lambda s: s.props["rcmode"])
  hwformat      = property(lambda s: s.props["hwformat"])
  format        = property(lambda s: s.props["format"])
  frames        = property(lambda s: s.props["frames"])
  width         = property(lambda s: s.props["width"])
  height        = property(lambda s: s.props["height"])
  source        = property(lambda s: s.props["source"])
  encoded       = property(lambda s: s.props["encoded"])

  # optional properties
  gstparser     = property(lambda s: s.ifprop("gstparser", " ! {gstparser}"))
  gstmuxer      = property(lambda s: s.ifprop("gstmuxer", " ! {gstmuxer}"))
  fps           = property(lambda s: s.ifprop("fps", " framerate={fps}"))
  profile       = property(lambda s: s.ifprop("profile", ",profile={profile}"))

  @property
  def lowpower(self):
    def inner(lowpower):
      return f" tune={'low-power' if lowpower else 'none'}"
    return self.ifprop("lowpower", inner)

  @timefn("gst-encode")
  def encode(self):
    return call(
      f"gst-launch-1.0 -vf filesrc location={self.source} num-buffers={self.frames}"
      f" ! rawvideoparse format={self.format} width={self.width} height={self.height}{self.fps}"
      f" ! videoconvert chroma-mode=none dither=0 ! video/x-raw,format={self.hwformat}"
      f" ! {self.gstencoder} ! {self.gstmediatype}{self.profile}{self.gstparser}{self.gstmuxer}"
      f" ! filesink location={self.encoded}"
    )

@slash.requires(have_gst)
@slash.requires(*have_gst_element("checksumsink2"))
class BaseEncoderTest(slash.Test):
  EncoderClass = Encoder
  DecoderClass = Decoder

  def before(self):
    super().before()
    self.refctx = []
    self.post_validate = lambda: None

  def map_profile(self):
    raise NotImplementedError

  def get_file_ext(self):
    raise NotImplementedError

  def gen_name(self):
    name = "{case}-{rcmode}"
    if vars(self).get("profile", None) is not None:
      name += "-{profile}"
    if vars(self).get("fps", None) is not None:
      name += "-{fps}"
    if vars(self).get("gop", None) is not None:
      name += "-{gop}"
    if vars(self).get("qp", None) is not None:
      name += "-{qp}"
    if vars(self).get("slices", None) is not None:
      name += "-{slices}"
    if vars(self).get("tilecols", None) is not None:
      name += "-{tilecols}"
    if vars(self).get("tilerows", None) is not None:
      name += "-{tilerows}"
    if vars(self).get("quality", None) is not None:
      name += "-{quality}"
    if vars(self).get("bframes", None) is not None:
      name += "-{bframes}"
    if vars(self).get("minrate", None) is not None:
      name += "-{minrate}k"
    if vars(self).get("maxrate", None) is not None:
      name += "-{maxrate}k"
    if vars(self).get("refmode", None) is not None:
      name += "-{refmode}"
    if vars(self).get("refs", None) is not None:
      name += "-{refs}"
    if vars(self).get("lowpower", False):
      name += "-low-power"
    if vars(self).get("loopshp", None) is not None:
      name += "-{loopshp}"
    if vars(self).get("looplvl", None) is not None:
      name += "-{looplvl}"
    if vars(self).get("ladepth", None) is not None:
      name += "-{ladepth}"
    if vars(self).get("r2r", None) is not None:
      name += "-r2r"

    return name

  def validate_caps(self):
    skip_test_if_missing_features(self)

    self.encoder = self.EncoderClass(**vars(self))
    self.decoder = self.DecoderClass(
      gstdecoder  = self.gstdecoder,
      gstparser   = vars(self).get("gstparser", None),
      gstdemuxer  = vars(self).get("gstdemuxer", None),
      frames      = self.frames,
      format      = self.format,
    )

    if None in [self.encoder.hwformat, self.encoder.format, self.decoder.format]:
      slash.skip_test("{format} format not supported".format(**vars(self)))

    maxw, maxh = self.caps["maxres"]
    if self.width > maxw or self.height > maxh:
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{width}x{height} not supported", **vars(self)))

    if vars(self).get("slices", 1) > 1 and not self.caps.get("multislice", True):
      slash.skip_test(
        format_value(
          "{platform}.{driver}.slice > 1 unsupported in this mode", **vars(self)))

    if not self.caps.get(self.rcmode, True):
      slash.skip_test(
        format_value(
          "{platform}.{driver}.{rcmode} unsupported in this mode", **vars(self)))

    if vars(self).get("profile", None) is not None:
      self.mprofile = self.map_profile()
      if self.mprofile is None:
        slash.skip_test("{profile} profile is not supported".format(**vars(self)))
      self.encoder.update(profile = self.mprofile)

    self.post_validate()

  def encode(self):
    self.validate_caps()

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    name  = self.gen_name().format(**vars(self))
    ext   = self.get_file_ext()

    self.encoder.update(
      encoded = get_media()._test_artifact("{}.{}".format(name, ext)))
    self.encoder.encode()

    if vars(self).get("r2r", None) is not None:
      assert type(self.r2r) is int and self.r2r > 1, "invalid r2r value"
      md5ref = self.md5_demuxed()
      get_media()._set_test_details(md5_ref = md5ref)
      for i in range(1, self.r2r):
        self.encoder.update(
          encoded = get_media()._test_artifact("{}_{}.{}".format(name, i, ext)))
        self.encoder.encode()
        result = self.md5_demuxed()
        get_media()._set_test_details(**{"md5_{:03}".format(i): result})
        assert md5ref == result, "r2r md5 mismatch"
        # delete encoded file after each iteration
        get_media()._purge_test_artifact(self.encoder.encoded)
    else:
      self.check_bitrate()
      self.check_metrics()

  def check_metrics(self):
    name = (self.gen_name() + "-{width}x{height}-{format}").format(**vars(self))
    self.decoder.update(
      source      = self.encoder.encoded,
      decoded     = get_media()._test_artifact("{}.yuv".format(name)),
    )
    self.decoder.decode()

    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.source, self.decoder.decoded,
        self.width, self.height,
        self.frames, self.format),
      context = self.refctx,
    )

  def check_bitrate(self):
    encsize = os.path.getsize(self.encoder.encoded)
    bitrate_actual = encsize * 8 * vars(self).get("fps", 25) / 1024.0 / self.frames
    get_media()._set_test_details(
      size_encoded = encsize,
      bitrate_actual = "{:-.2f}".format(bitrate_actual))

    if "cbr" == self.rcmode:
      bitrate_gap = abs(bitrate_actual - self.bitrate) / self.bitrate
      get_media()._set_test_details(bitrate_gap = "{:.2%}".format(bitrate_gap))

      # acceptable bitrate within 10% of bitrate
      assert(bitrate_gap <= 0.10)

    elif self.rcmode in ["vbr", "la_vbr"]:
      # acceptable bitrate within 25% of minrate and 10% of maxrate
      assert(self.minrate * 0.75 <= bitrate_actual <= self.maxrate * 1.10)

  def md5_demuxed(self):
    # gstreamer muxers write timestamps to container header and will be
    # different in each r2r iteration.  Thus, extract the elementary video
    # stream from the container and take md5 on the elementary video stream.
    if vars(self).get("gstdemuxer", None) is not None:
      demuxed = get_media()._test_artifact(f"{self.encoder.encoded}.{self.codec}")
      call(
        f"gst-launch-1.0 -vf filesrc location={self.encoder.encoded}"
        f" ! queue ! {self.gstdemuxer} name=dmux dmux.video_0 ! queue"
        f" ! filesink location={demuxed}"
      )
      result = md5(demuxed)
      get_media()._purge_test_artifact(demuxed)
      return result
    return md5(self.encoder.encoded)
