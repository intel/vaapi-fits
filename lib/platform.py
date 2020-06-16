###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from __future__ import absolute_import
from .common import memoize
import os

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

  from .common import get_media
  plinfo = dict()
  infofile = os.path.abspath(
    os.path.join(
      os.path.dirname(__file__), "caps",
      str(get_media()._get_platform_name()),
      "info"
    )
  )
  if os.path.exists(infofile):
    with open(infofile, 'rb') as f:
      exec(f.read(), plinfo)

  return dict(
    node = str(platform.node()),
    kernel = str(platform.release()),
    dist = str(linux_dist()),
    cpu = cpu,
    driver = str(get_media()._get_driver_name()),
    platform = str(get_media()._get_platform_name()),
    **plinfo.get("info", dict()),
  )
