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

class CodecLevel(IntEnum):
    MFX_LEVEL_UNKNOWN                       =0 #/*!< Unspecified level. */
    #/* H.264 level 1-1.3 */
    MFX_LEVEL_AVC_1                         =10
    MFX_LEVEL_AVC_1b                        =9
    MFX_LEVEL_AVC_11                        =11
    MFX_LEVEL_AVC_12                        =12
    MFX_LEVEL_AVC_13                        =13
    #/* H.264 level 2-2.2 */
    MFX_LEVEL_AVC_2                         =20
    MFX_LEVEL_AVC_21                        =21
    MFX_LEVEL_AVC_22                        =22
    #/* H.264 level 3-3.2 */
    MFX_LEVEL_AVC_3                         =30
    MFX_LEVEL_AVC_31                        =31
    MFX_LEVEL_AVC_32                        =32
    #/* H.264 level 4-4.2 */
    MFX_LEVEL_AVC_4                         =40
    MFX_LEVEL_AVC_41                        =41
    MFX_LEVEL_AVC_42                        =42
    #/* H.264 level 5-5.2 */
    MFX_LEVEL_AVC_5                         =50
    MFX_LEVEL_AVC_51                        =51
    MFX_LEVEL_AVC_52                        =52
    #/* H.264 level 6-6.2 */
    MFX_LEVEL_AVC_6                         =60
    MFX_LEVEL_AVC_61                        =61
    MFX_LEVEL_AVC_62                        =62

    #/* HEVC levels */
    MFX_LEVEL_HEVC_1   = 10
    MFX_LEVEL_HEVC_2   = 20
    MFX_LEVEL_HEVC_21  = 21
    MFX_LEVEL_HEVC_3   = 30
    MFX_LEVEL_HEVC_31  = 31
    MFX_LEVEL_HEVC_4   = 40
    MFX_LEVEL_HEVC_41  = 41
    MFX_LEVEL_HEVC_5   = 50
    MFX_LEVEL_HEVC_51  = 51
    MFX_LEVEL_HEVC_52  = 52
    MFX_LEVEL_HEVC_6   = 60
    MFX_LEVEL_HEVC_61  = 61
    MFX_LEVEL_HEVC_62  = 62

    #/* AV1 Levels */
    MFX_LEVEL_AV1_2                         = 20
    MFX_LEVEL_AV1_21                        = 21
    MFX_LEVEL_AV1_22                        = 22
    MFX_LEVEL_AV1_23                        = 23
    MFX_LEVEL_AV1_3                         = 30
    MFX_LEVEL_AV1_31                        = 31
    MFX_LEVEL_AV1_32                        = 32
    MFX_LEVEL_AV1_33                        = 33
    MFX_LEVEL_AV1_4                         = 40
    MFX_LEVEL_AV1_41                        = 41
    MFX_LEVEL_AV1_42                        = 42
    MFX_LEVEL_AV1_43                        = 43
    MFX_LEVEL_AV1_5                         = 50
    MFX_LEVEL_AV1_51                        = 51
    MFX_LEVEL_AV1_52                        = 52
    MFX_LEVEL_AV1_53                        = 53
    MFX_LEVEL_AV1_6                         = 60
    MFX_LEVEL_AV1_61                        = 61
    MFX_LEVEL_AV1_62                        = 62
    MFX_LEVEL_AV1_63                        = 63
    MFX_LEVEL_AV1_7                         = 70
    MFX_LEVEL_AV1_71                        = 71
    MFX_LEVEL_AV1_72                        = 72
    MFX_LEVEL_AV1_73                        = 73


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
