###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from __future__ import absolute_import
from .common import memoize
import os

ALL_PLATFORMS                  = [
  "IVB", "BYT", "HSW", "BDW",
  "BSW", "SKL", "APL", "KBL",
  "GLK", "CFL", "WHL", "ICL",
]
JPEG_DECODE_PLATFORMS          = []
JPEG_ENCODE_PLATFORMS          = []
MPEG2_DECODE_PLATFORMS         = []
MPEG2_ENCODE_PLATFORMS         = []
VC1_DECODE_PLATFORMS           = []
AVC_DECODE_PLATFORMS           = []
AVC_ENCODE_PLATFORMS           = []
AVC_ENCODE_CQP_LP_PLATFORMS    = []
AVC_ENCODE_CBRVBR_LP_PLATFORMS = []
HEVC_DECODE_8BIT_PLATFORMS     = []
HEVC_DECODE_8BIT_8K_PLATFORMS  = []
HEVC_DECODE_8BIT_422_PLATFORMS = []
HEVC_DECODE_8BIT_444_PLATFORMS = []
HEVC_ENCODE_8BIT_PLATFORMS     = []
HEVC_ENCODE_8BIT_LP_PLATFORMS  = []
HEVC_DECODE_10BIT_PLATFORMS    = []
HEVC_ENCODE_10BIT_PLATFORMS    = []
HEVC_ENCODE_10BIT_LP_PLATFORMS = []
VP8_DECODE_PLATFORMS           = []
VP8_ENCODE_PLATFORMS           = []
VP9_DECODE_8BIT_PLATFORMS      = []
VP9_ENCODE_8BIT_PLATFORMS      = []
VP9_DECODE_10BIT_PLATFORMS     = []
VP9_ENCODE_10BIT_PLATFORMS     = []
DECODE_10BIT_422_PLATFORMS     = []
DECODE_10BIT_444_PLATFORMS     = []
VPP_PLATFORMS                  = []
VPP_TRANSFORM_PLATFORMS        = []

driver = os.environ.get("LIBVA_DRIVER_NAME", None) or "i965"

if "i965" == driver:
  JPEG_DECODE_PLATFORMS         = [       "BYT", "HSW", "BDW", "BSW", "SKL", "APL", "KBL", "GLK", "CFL", "WHL"]
  JPEG_ENCODE_PLATFORMS         = [                                   "SKL", "APL", "KBL", "GLK", "CFL", "WHL"]
  MPEG2_DECODE_PLATFORMS        = [       "BYT", "HSW", "BDW", "BSW", "SKL", "APL", "KBL", "GLK", "CFL", "WHL"]
  MPEG2_ENCODE_PLATFORMS        = ["IVB", "BYT", "HSW", "BDW", "BSW", "SKL",        "KBL",        "CFL", "WHL"]
  VC1_DECODE_PLATFORMS          = [       "BYT", "HSW", "BDW", "BSW", "SKL", "APL", "KBL", "GLK", "CFL", "WHL"]
  AVC_DECODE_PLATFORMS          = [       "BYT", "HSW", "BDW", "BSW", "SKL", "APL", "KBL", "GLK", "CFL", "WHL"]
  AVC_ENCODE_PLATFORMS          = ["IVB", "BYT", "HSW", "BDW", "BSW", "SKL", "APL", "KBL", "GLK", "CFL", "WHL"]
  AVC_ENCODE_CQP_LP_PLATFORMS   = [                                   "SKL", "APL", "KBL",        "CFL", "WHL"]
  HEVC_DECODE_8BIT_PLATFORMS    = [                            "BSW", "SKL", "APL", "KBL", "GLK", "CFL", "WHL"]
  HEVC_ENCODE_8BIT_PLATFORMS    = [                                   "SKL", "APL", "KBL", "GLK", "CFL", "WHL"]
  HEVC_DECODE_10BIT_PLATFORMS   = [                                          "APL", "KBL", "GLK", "CFL", "WHL"]
  HEVC_ENCODE_10BIT_PLATFORMS   = [                                                 "KBL", "GLK", "CFL", "WHL"]
  VP8_DECODE_PLATFORMS          = [                     "BDW", "BSW", "SKL", "APL", "KBL", "GLK", "CFL", "WHL"]
  VP8_ENCODE_PLATFORMS          = [                                   "SKL", "APL", "KBL", "GLK", "CFL", "WHL"]
  VP9_DECODE_8BIT_PLATFORMS     = [                                          "APL", "KBL", "GLK", "CFL", "WHL"]
  VP9_ENCODE_8BIT_PLATFORMS     = [                                                 "KBL", "GLK", "CFL", "WHL"]
  VP9_DECODE_10BIT_PLATFORMS    = [                                                 "KBL", "GLK", "CFL", "WHL"]
  VPP_PLATFORMS                 = ["IVB", "BYT", "HSW", "BDW", "BSW", "SKL", "APL", "KBL", "GLK", "CFL", "WHL"]

elif "iHD" == driver:
  JPEG_DECODE_PLATFORMS          = [                    "BDW",        "SKL", "APL", "KBL",        "CFL", "WHL", "ICL"]
  JPEG_ENCODE_PLATFORMS          = [                                  "SKL", "APL", "KBL",        "CFL", "WHL", "ICL"]
  MPEG2_DECODE_PLATFORMS         = [                    "BDW",        "SKL", "APL", "KBL",        "CFL", "WHL", "ICL"]
  MPEG2_ENCODE_PLATFORMS         = [                    "BDW",        "SKL",        "KBL",        "CFL", "WHL", "ICL"]
  VC1_DECODE_PLATFORMS           = [                    "BDW",        "SKL", "APL", "KBL",        "CFL", "WHL", "ICL"]
  AVC_DECODE_PLATFORMS           = [                    "BDW",        "SKL", "APL", "KBL",        "CFL", "WHL", "ICL"]
  AVC_ENCODE_PLATFORMS           = [                    "BDW",        "SKL", "APL", "KBL",        "CFL", "WHL", "ICL"]
  AVC_ENCODE_CQP_LP_PLATFORMS    = [                                  "SKL", "APL", "KBL",        "CFL", "WHL", "ICL"]
  AVC_ENCODE_CBRVBR_LP_PLATFORMS = [                                                                            "ICL"]
  HEVC_DECODE_8BIT_PLATFORMS     = [                                  "SKL", "APL", "KBL",        "CFL", "WHL", "ICL"]
  HEVC_DECODE_8BIT_8K_PLATFORMS  = [                                  "SKL", "APL", "KBL",        "CFL", "WHL", "ICL"]
  HEVC_DECODE_8BIT_422_PLATFORMS = [                                                                            "ICL"]
  HEVC_DECODE_8BIT_444_PLATFORMS = [                                                                            "ICL"]
  HEVC_ENCODE_8BIT_PLATFORMS     = [                                  "SKL", "APL", "KBL",        "CFL", "WHL", "ICL"]
  HEVC_ENCODE_8BIT_LP_PLATFORMS  = [                                                                            "ICL"]
  HEVC_DECODE_10BIT_PLATFORMS    = [                                         "APL", "KBL",        "CFL", "WHL", "ICL"]
  HEVC_ENCODE_10BIT_PLATFORMS    = [                                                "KBL",        "CFL", "WHL", "ICL"]
  HEVC_ENCODE_10BIT_LP_PLATFORMS = [                                                                            "ICL"]
  VP8_DECODE_PLATFORMS           = [                    "BDW",        "SKL", "APL", "KBL",        "CFL", "WHL", "ICL"]
  VP8_ENCODE_PLATFORMS           = [                                                "KBL",        "CFL", "WHL", "ICL"]
  VP9_DECODE_8BIT_PLATFORMS      = [                                         "APL", "KBL",        "CFL", "WHL", "ICL"]
  VP9_ENCODE_8BIT_PLATFORMS      = [                                                                            "ICL"]
  VP9_DECODE_10BIT_PLATFORMS     = [                                                "KBL",        "CFL", "WHL", "ICL"]
  VP9_ENCODE_10BIT_PLATFORMS     = [                                                                            "ICL"]
  DECODE_10BIT_422_PLATFORMS     = [                                                                            "ICL"]
  DECODE_10BIT_444_PLATFORMS     = [                                                                            "ICL"]
  VPP_PLATFORMS                  = [                    "BDW",        "SKL", "APL", "KBL",        "CFL", "WHL", "ICL"]
  VPP_TRANSFORM_PLATFORMS        = VPP_PLATFORMS

@memoize
def load_caps():
  from .common import get_media
  namespace = dict(
    res2k   = ( 2048,  2048),
    res4k   = ( 4096,  4096),
    res8k   = ( 8192,  8192),
    res16k  = (16384, 16384),
  )
  capsfile = os.path.abspath(
    os.path.join(
      os.path.dirname(__file__), "caps",
      str(get_media()._get_platform_name()),
      str(get_media()._get_driver_name()),
    )
  )
  if os.path.exists(capsfile):
    execfile(capsfile, namespace)
  caps = namespace.get("caps", None)

  # map some aliases for convenience
  if caps is not None:
    if caps.get("vpp", dict()).get("procamp", None) is not None:
      for op in ["brightness", "contrast", "hue", "saturation"]:
        caps["vpp"].setdefault(op, caps["vpp"]["procamp"])
    if caps.get("vpp", dict()).get("transpose", None) is not None:
      for op in ["mirroring", "rotation"]:
        caps["vpp"].setdefault(op, caps["vpp"]["transpose"])
    di = caps.get("vpp", dict()).get("deinterlace", dict())
    if di.get("motion_adaptive", None) is not None:
      di.setdefault("advanced", di["motion_adaptive"])

  return caps

@memoize
def get_caps(*args):
  caps = load_caps()
  for key in args:
    if caps is None:
      break
    caps = caps.get(key, None)
  return caps

@memoize
def have_caps(*args):
  from .common import get_media
  failmsg = "{0}.{1}.{2} caps".format(
    get_media()._get_platform_name(),
    get_media()._get_driver_name(),
    '.'.join(args)
  )
  return get_caps(*args) is not None, failmsg

def platform_tags(platforms):
  def wrap(f):
    import slash
    for platform in platforms:
      f = slash.tag(platform)(f)
    return f
  return wrap

def info():
  import platform
  try:
    import cpuinfo
    cpu = cpuinfo.get_cpu_info()["brand"]
  except:
    cpu = "unknown"

  return dict(
    node = str(platform.node()),
    kernel = str(platform.release()),
    dist = str(platform.dist()),
    cpu = cpu,
  )
