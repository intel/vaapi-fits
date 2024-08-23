from ...lib.codecs import Codec
from ...lib.common import memoize
from ...lib.properties import PropertyHandler
from enum import IntEnum, unique

#define come from _install/include/vpl/mfxstructures.h
class CodecProfile(IntEnum):
    MFX_PROFILE_UNKNOWN                     =0 #/*!< Unspecified profile. */

    #/* Combined with H.264 profile these flags impose additional constrains. See H.264 specification for the list of constrains. */
    MFX_PROFILE_AVC_CONSTRAINT_SET0     = (0x100 << 0)
    MFX_PROFILE_AVC_CONSTRAINT_SET1     = (0x100 << 1)
    MFX_PROFILE_AVC_CONSTRAINT_SET2     = (0x100 << 2)
    MFX_PROFILE_AVC_CONSTRAINT_SET3     = (0x100 << 3)
    MFX_PROFILE_AVC_CONSTRAINT_SET4     = (0x100 << 4)
    MFX_PROFILE_AVC_CONSTRAINT_SET5     = (0x100 << 5)

    #/* H.264 Profiles. */
    MFX_PROFILE_AVC_BASELINE                =66
    MFX_PROFILE_AVC_MAIN                    =77
    MFX_PROFILE_AVC_EXTENDED                =88
    MFX_PROFILE_AVC_HIGH                    =100
    MFX_PROFILE_AVC_HIGH10                  =110
    MFX_PROFILE_AVC_HIGH_422                =122
    MFX_PROFILE_AVC_CONSTRAINED_BASELINE    =MFX_PROFILE_AVC_BASELINE + MFX_PROFILE_AVC_CONSTRAINT_SET1
    MFX_PROFILE_AVC_CONSTRAINED_HIGH        =MFX_PROFILE_AVC_HIGH     + MFX_PROFILE_AVC_CONSTRAINT_SET4 + MFX_PROFILE_AVC_CONSTRAINT_SET5
    MFX_PROFILE_AVC_PROGRESSIVE_HIGH        =MFX_PROFILE_AVC_HIGH     + MFX_PROFILE_AVC_CONSTRAINT_SET4

    #/* HEVC profiles */
    MFX_PROFILE_HEVC_MAIN             =1
    MFX_PROFILE_HEVC_MAIN10           =2
    MFX_PROFILE_HEVC_MAINSP           =3
    MFX_PROFILE_HEVC_REXT             =4
    MFX_PROFILE_HEVC_SCC              =9

    #/* AV1 Profiles */
    MFX_PROFILE_AV1_MAIN                    = 1
    MFX_PROFILE_AV1_HIGH                    = 2
    MFX_PROFILE_AV1_PRO                     = 3

    #/* VP9 Profiles */
    MFX_PROFILE_VP9_0                       = 1
    MFX_PROFILE_VP9_1                       = 2
    MFX_PROFILE_VP9_2                       = 3
    MFX_PROFILE_VP9_3                       = 4

class RateControlMethod(IntEnum):
#/*! The RateControlMethod enumerator itemizes bitrate control methods. */
    MFX_RATECONTROL_CBR       =1 #/*!< Use the constant bitrate control algorithm. */
    MFX_RATECONTROL_VBR       =2 #/*!< Use the variable bitrate control algorithm. */
    MFX_RATECONTROL_CQP       =3 #/*!< Use the constant quantization parameter algorithm. */
    MFX_RATECONTROL_AVBR      =4 #/*!< Use the average variable bitrate control algorithm. */
    MFX_RATECONTROL_RESERVED1 =5
    MFX_RATECONTROL_RESERVED2 =6
    MFX_RATECONTROL_RESERVED3 =100
    MFX_RATECONTROL_RESERVED4 =7
    #/*!
    #   Use the VBR algorithm with look ahead. It is a special bitrate control mode in the AVC encoder that has been designed
    #   to improve encoding quality. It works by performing extensive analysis of several dozen frames before the actual encoding and as a side
    #   effect significantly increases encoding delay and memory consumption.

    #   The only available rate control parameter in this mode is mfxInfoMFX::TargetKbps. Two other parameters, MaxKbps and InitialDelayInKB,
    #   are ignored. To control LA depth the application can use mfxExtCodingOption2::LookAheadDepth parameter.

    #   This method is not HRD compliant.
    #*/
    MFX_RATECONTROL_LA        =8
    #/*!
    #   Use the Intelligent Constant Quality algorithm. This algorithm improves subjective video quality of encoded stream. Depending on content,
    #   it may or may not decrease objective video quality. Only one control parameter is used - quality factor, specified by mfxInfoMFX::ICQQuality.
    #*/
    MFX_RATECONTROL_ICQ       =9
    #/*!
    #   Use the Video Conferencing Mode algorithm. This algorithm is similar to the VBR and uses the same set of parameters mfxInfoMFX::InitialDelayInKB,
    #   TargetKbpsandMaxKbps. It is tuned for IPPP GOP pattern and streams with strong temporal correlation between frames.
    #   It produces better objective and subjective video quality in these conditions than other bitrate control algorithms.
    #   It does not support interlaced content, B-frames and produced stream is not HRD compliant.
    #*/
    MFX_RATECONTROL_VCM       =10
    #/*!
    #   Use Intelligent Constant Quality algorithm with look ahead. Quality factor is specified by mfxInfoMFX::ICQQuality.
    #   To control LA depth the application can use mfxExtCodingOption2::LookAheadDepth parameter.
    #
    #   This method is not HRD compliant.
    #*/
    MFX_RATECONTROL_LA_ICQ    =11
    #/*!
    #   MFX_RATECONTROL_LA_EXT has been removed
    #*/

    #/*! Use HRD compliant look ahead rate control algorithm. */
    MFX_RATECONTROL_LA_HRD    =13
    #/*!
    #   Use the variable bitrate control algorithm with constant quality. This algorithm trying to achieve the target subjective quality with
    #   the minimum number of bits, while the bitrate constraint and HRD compliance are satisfied. It uses the same set of parameters
    #   as VBR and quality factor specified by mfxExtCodingOption3::QVBRQuality.
    #*/
    MFX_RATECONTROL_QVBR      =14

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
        "high"      : CodecProfile.MFX_PROFILE_AVC_HIGH,
        "main"      : CodecProfile.MFX_PROFILE_AVC_MAIN,
        "baseline"  : CodecProfile.MFX_PROFILE_AVC_BASELINE,
        "unknown"   : CodecProfile.MFX_PROFILE_UNKNOWN
      },
      Codec.HEVC   : {
        "main"        : CodecProfile.MFX_PROFILE_HEVC_MAIN,
        "main444"     : CodecProfile.MFX_PROFILE_HEVC_REXT,
        "scc"         : CodecProfile.MFX_PROFILE_HEVC_SCC,
        "scc-444"     : CodecProfile.MFX_PROFILE_HEVC_SCC,
        "mainsp"      : CodecProfile.MFX_PROFILE_HEVC_MAINSP,
        "main10"      : CodecProfile.MFX_PROFILE_HEVC_MAIN10,
        "main10sp"    : CodecProfile.MFX_PROFILE_HEVC_MAINSP,
        "main444-10"  : CodecProfile.MFX_PROFILE_HEVC_REXT,
        "unknown"     : CodecProfile.MFX_PROFILE_UNKNOWN
      },
      Codec.AV1 : {
        "main"  : CodecProfile.MFX_PROFILE_AV1_MAIN,
      },
      Codec.VP9 : {
        "profile0"  : CodecProfile.MFX_PROFILE_VP9_0,
        "profile1"  : CodecProfile.MFX_PROFILE_VP9_1,
        "profile2"  : CodecProfile.MFX_PROFILE_VP9_2,
        "profile3"  : CodecProfile.MFX_PROFILE_VP9_3
      },
    }[codec][profile]

  @classmethod
  @memoize
  def map_rcmode(cls, rcmode):
    # TODO: we could move this method to the enum class as "lookup"
    # then call MfxRateControlMethod.lookup(rcmode)
    return {
      "CQP" : RateControlMethod.MFX_RATECONTROL_CQP,
      "CBR" : RateControlMethod.MFX_RATECONTROL_CBR,
      "VBR" : RateControlMethod.MFX_RATECONTROL_VBR,
      "ICQ" : RateControlMethod.MFX_RATECONTROL_ICQ,
    }[rcmode.upper()]
