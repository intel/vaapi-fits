###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from __future__ import absolute_import
from .common import memoize
import os

@memoize
def load_caps_file(capsfile):
  namespace = dict(
    res2k   = ( 2048,  2048),
    res4k   = ( 4096,  4096),
    res8k   = ( 8192,  8192),
    res16k  = (16384, 16384),
  )

  if os.path.exists(capsfile):
    with open(capsfile, 'rb') as f:
      exec(f.read(), namespace)

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
def load_caps():
  from .common import get_media
  from slash import logger

  pname = str(get_media()._get_platform_name())
  dname = str(get_media()._get_driver_name())

  # user caps
  usercaps = os.environ.get("VAAPI_FITS_CAPS", None)
  if usercaps is not None:
    capsfile = os.path.abspath(
      os.path.join(usercaps, pname, dname)
    )
    caps = load_caps_file(capsfile)
    if caps is not None:
      logger.notice("Using user caps")
      return caps

  # library caps
  capsfile = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "caps", pname, dname)
  )

  logger.notice("Using library caps")
  return load_caps_file(capsfile)

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

@memoize
def load_capsinfo_file(infofile):
  namespace = dict()

  if os.path.exists(infofile):
    with open(infofile, 'rb') as f:
      exec(f.read(), namespace)

  return namespace.get("info", None)

@memoize
def load_capsinfo():
  from .common import get_media

  pname = str(get_media()._get_platform_name())

  # user caps info
  usercaps = os.environ.get("VAAPI_FITS_CAPS", None)
  if usercaps is not None:
    infofile = os.path.abspath(
      os.path.join(usercaps, pname, "info")
    )
    capsinfo = load_capsinfo_file(infofile)
    if capsinfo is not None:
      return capsinfo

  # library caps info
  infofile = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "caps", pname, "info")
  )

  return load_capsinfo_file(infofile)

@memoize
def info():
  import platform
  try:
    from distro import linux_distribution as linux_dist
  except:
    try:
      from platform import dist as linux_dist
    except:
      linux_dist = lambda: "unknown"

  try:
    import cpuinfo
    cpu = cpuinfo.get_cpu_info()["brand"]
  except:
    cpu = "unknown"

  # python load from WSL1: 'linux-{kernel_version}-microsoft-{architecture}-with-{glibc_version}'
  # python load from WSL2: 'linux-{kernel_version}-microsoft-standard-{architecture}-with-{glibc_version}'
  # python load from OS native: 'windows-{os_family}_{os_version}-{patch_version}'
  if 'microsoft' in platform.platform().lower():
    os='wsl'
  else:
    os='linux'

  from .common import get_media

  capsinfo = load_capsinfo() or dict()

  return dict(
    node = str(platform.node()),
    kernel = str(platform.release()),
    dist = str(linux_dist()),
    cpu = cpu,
    driver = str(get_media()._get_driver_name()),
    platform = str(get_media()._get_platform_name()),
    os = os,
    **capsinfo,
  )
