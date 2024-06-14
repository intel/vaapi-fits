from ...lib.codecs import Codec
from ...lib.common import memoize
from ...lib.properties import PropertyHandler

# TODO: move string_api enums to this file
# NOTE/FIXME: these enums need to derive from IntEnum, not Enum
from ...lib.string_api import CodecProfile as MfxCodecProfile
from ...lib.string_api import CodecLevel as MfxCodecLevel
from ...lib.string_api import RateControlMethod as MfxRateControlMethod

class StringAPI(PropertyHandler):
  level   = property(lambda s: s.ifprop("level", "CodecLevel={level}"))
  gop     = property(lambda s: s.ifprop("gop", "GopPicSize={gop}"))
  bframes = property(lambda s: s.ifprop("bframes", "GopRefDist={bframes}"))
  slices  = property(lambda s: s.ifprop("slices", "NumSlice={slices}"))
  minrate = property(lambda s: s.ifprop("minrate", "TargetKbps={minrate}"))
  maxrate = property(lambda s: s.ifprop("maxrate", "MaxKbps={maxrate}"))
  refs    = property(lambda s: s.ifprop("refs", "NumRefFrame={refs}"))
  ladepth = property(lambda s: s.ifprop("ladepth", "LookAheadDepth={ladepth}"))
  extbrc  = property(lambda s: s.ifprop("extbrc", "ExtBRC={extbrc}"))
  ldb     = property(lambda s: s.ifprop("ldb", "mfxExtCodingOption3.LowDelayBRC={ldb}"))
  strict  = property(lambda s: s.ifprop("strict", "GopOptFlag={strict}"))
  pict    = property(lambda s: s.ifprop("vpict", "mfxExtCodingOption.PicTimingSEI=0"))
  quality = property(lambda s: s.ifprop("quality", "TargetUsage={quality}"))
  lowpower  = property(lambda s: s.ifprop("lowpower", "LowPower={lowpower}"))
  tilecols  = property(lambda s: s.ifprop("tilecols", "mfxExtAV1TileParam.NumTileColumns={tilecols}"))
  tilerows  = property(lambda s: s.ifprop("tilerows", "mfxExtAV1TileParam.NumTileRows={tilerows}"))
  maxframesize  = property(lambda s: s.ifprop("maxframesize", "MaxSliceSize={maxframesize}"))

  @property
  def profile(self):
    def inner(profile):
      return f"CodecProfile={self.map_profile(self.codec, self.props['profile'])}"
    return self.ifprop("profile", inner)

  @property
  def rcmode(self):
    return f"RateControlMethod={self.map_rcmode(self.props['rcmode'])}"

  @property
  def level(self):
    def inner(level):
      # TODO: need to define map_level
      return f"CodecLevel={self.map_level(self.props['level'])}"
    return self.ifprop("level", inner)

  @property
  def qp(self):
    def inner(qp):
      rcmode = self.props["rcmode"].upper()
      mqp = qp
      if self.codec in [Codec.MPEG2]:
        mqp = mapRangeInt(qp, [0, 100], [1, 51])
      elif self.codec in [Codec.AV1] and "ICQ" == rcmode:
        mqp = mapRangeInt(qp, [0, 255], [1, 51])
      elif self.codec in [Codec.HEVC] and "QVBR" == rcmode:
        mqp = mapRangeInt(qp, [0, 255], [1, 51])
      return f"QPI={mqp}:QPP={mqp}:QPB={mqp}"
    return self.ifprop("qp", inner)

  @property
  def encparams(self):
    params = [
      self.profile, self.rcmode, self.qp, self.level, self.gop, self.bframes,
      self.slices, self.minrate, self.maxrate, self.refs, self.ladepth,
      self.extbrc, self.ldb, self.strict, self.pict, self.quality, self.lowpower,
      self.tilecols, self.tilerows, self.maxframesize,
    ]
    return ':'.join(v for v in params if len(v) != 0)

  @classmethod
  @memoize
  def map_profile(cls, codec, profile):
    # TODO: we could move this method to the enum class as "lookup"
    # then call MfxCodecProfile.lookup(codec, profile)
    return {
      Codec.AVC     : {
        "high"      : MfxCodecProfile.MFX_PROFILE_AVC_HIGH,
        "main"      : MfxCodecProfile.MFX_PROFILE_AVC_MAIN,
        "baseline"  : MfxCodecProfile.MFX_PROFILE_AVC_BASELINE,
        "unknown"   : MfxCodecProfile.MFX_PROFILE_UNKNOWN
      },
      Codec.HEVC   : {
        "main"        : MfxCodecProfile.MFX_PROFILE_HEVC_MAIN,
        "main444"     : MfxCodecProfile.MFX_PROFILE_HEVC_REXT,
        "scc"         : MfxCodecProfile.MFX_PROFILE_HEVC_SCC,
        "scc-444"     : MfxCodecProfile.MFX_PROFILE_HEVC_SCC,
        "mainsp"      : MfxCodecProfile.MFX_PROFILE_HEVC_MAINSP,
        "main10"      : MfxCodecProfile.MFX_PROFILE_HEVC_MAIN10,
        "main10sp"    : MfxCodecProfile.MFX_PROFILE_HEVC_MAINSP,
        "main444-10"  : MfxCodecProfile.MFX_PROFILE_HEVC_REXT,
        "unknown"     : MfxCodecProfile.MFX_PROFILE_UNKNOWN
      },
      Codec.AV1 : {
        "main"  : MfxCodecProfile.MFX_PROFILE_AV1_MAIN,
      },
      Codec.VP9 : {
        "profile0"  : MfxCodecProfile.MFX_PROFILE_VP9_0,
        "profile1"  : MfxCodecProfile.MFX_PROFILE_VP9_1,
        "profile2"  : MfxCodecProfile.MFX_PROFILE_VP9_2,
        "profile3"  : MfxCodecProfile.MFX_PROFILE_VP9_3
      },
    }[codec][profile]

  @classmethod
  @memoize
  def map_rcmode(cls, rcmode):
    # TODO: we could move this method to the enum class as "lookup"
    # then call MfxRateControlMethod.lookup(rcmode)
    return {
      "CQP" : MfxRateControlMethod.MFX_RATECONTROL_CQP,
      "CBR" : MfxRateControlMethod.MFX_RATECONTROL_CBR,
      "VBR" : MfxRateControlMethod.MFX_RATECONTROL_VBR,
      "ICQ" : MfxRateControlMethod.MFX_RATECONTROL_ICQ,
    }[rcmode.upper()]

# Example:
#
# <file lib/ffmpeg/qsv/encoder.py>
#
# # NOTE: Inherit from the StringAPI class first so that it overrides the
# # Encoder class
# from ....lib.mfx.api import StringAPI
# class StringAPIEncoder(StringAPI, Encoder):
#   @property
#   def encparams(self):
#     return f" -qsv_params '{super().encparams}'"
#
# <file test/ffmpeg-qsv/encode/hevc.py>
#
# from ....lib.ffmpeg.qsv.encoder import StringAPIEncoder
# class cqp(HEVC8EncoderTest):
#   ...
#   @slash.requires(*have_string_api) # TODO: define have_string_api
#   @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main']))
#   def test_strapi(self, case, gop, slices, bframes, qp, quality, profile):
#     self.EncoderClass = StringAPIEncoder
#     self.init(spec, case, gop, slices, bframes, qp, quality, profile)
#     self.encode()
#
#
