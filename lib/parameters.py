###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import copy
import itertools

def format_value(value, **params):
  from .common import get_media
  import types

  if type(value) is types.FunctionType:
    return format_value(value(), **params)

  augmented = dict(
    driver = get_media()._get_driver_name(),
    platform = get_media()._get_platform_name(),
  )
  augmented.update(**params)

  return value.format(**augmented)

def gen_avc_cqp_variants(spec, profiles, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = copy.deepcopy(params.get("variants", dict()).get("cqp_strapi", []))
    else:
      variants = copy.deepcopy(params.get("variants", dict()).get("cqp", None))
    
      if variants is None:
        keys = ["gop", "slices", "bframes", "qp", "quality", "profile"]
        product  = list(itertools.product([1], [1], [0], [14, 28], [1, 4, 7], profiles))  # I, single-slice
        product += list(itertools.product([30], [1], [0], [14, 28], [1, 4, 7], profiles)) # IP, single-slice
        product += list(itertools.product([30], [4], [2], [14, 28], [1, 4, 7], profiles)) # IPB, multi-slice
        variants = [dict(zip(keys, vals)) for vals in product]

    for variant in variants:
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles

      # backwards compatibility for ipbmode user config
      ipbmode = variant.get("ipbmode", None)
      if ipbmode is not None:
        assert not variant.get("gop", None)
        assert not variant.get("slices", None)
        assert not variant.get("bframes", None)
        variant.update(
          slices = 4 if ipbmode == 2 else 1,
          gop = 30 if ipbmode != 0 else 1,
          bframes = 2 if ipbmode == 2 else 0)

      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["bframes"],
          variant["qp"], variant["quality"], profile
        ]

def gen_avc_cqp_parameters(spec, profiles, strapi=False):
  keys = ("case", "gop", "slices", "bframes", "qp", "quality", "profile")
  params = gen_avc_cqp_variants(spec, profiles, strapi)
  return keys, params

def gen_avc_bdepth_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("bdepth", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      gop     = variant.get("gop", None)
      bframes = variant.get("bframes", None)
      bitrate = variant.get("bitrate", None)
      qp      = variant.get("qp", None)
      rcmode  = variant["rcmode"]
      if "cbr" == rcmode:
        variant.update(maxrate = bitrate)
      elif "vbr" == rcmode:
        variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, gop, bframes, bitrate, qp, variant["maxrate"],
          profile, rcmode, variant.get("bdepth", 1)
        ]

def gen_avc_bdepth_parameters(spec, profiles):
  keys = ("case", "gop", "bframes", "bitrate", "qp", "maxrate", "profile", "rcmode", "bdepth")
  params = gen_avc_bdepth_variants(spec, profiles)
  return keys, params

def gen_avc_bdepth_lp_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("bdepth_lp", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      gop     = variant.get("gop", None)
      bframes = variant.get("bframes", None)
      bitrate = variant.get("bitrate", None)
      qp      = variant.get("qp", None)
      rcmode  = variant["rcmode"]
      if "cbr" == rcmode:
        variant.update(maxrate = bitrate)
      elif "vbr" == rcmode:
        variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, gop, bframes, bitrate, qp, variant["maxrate"],
          profile, rcmode, variant.get("bdepth", 1)
        ]

def gen_avc_bdepth_lp_parameters(spec, profiles):
  keys = ("case", "gop", "bframes", "bitrate", "qp", "maxrate", "profile", "rcmode", "bdepth")
  params = gen_avc_bdepth_lp_variants(spec, profiles)
  return keys, params

def gen_avc_cbr_variants(spec, profiles, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = copy.deepcopy(params.get("variants", dict()).get("cbr_strapi", []))
    else:
      variants = copy.deepcopy(params.get("variants", dict()).get("cbr", []))
   
    for variant in variants:
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles

      # backwards compatibility for ipbmode user config
      ipbmode = variant.get("ipbmode", None)
      if ipbmode is not None:
        assert not variant.get("gop", None)
        assert not variant.get("slices", None)
        assert not variant.get("bframes", None)
        variant.update(
          slices = 4 if ipbmode == 2 else 1,
          gop = 30 if ipbmode != 0 else 1,
          bframes = 2 if ipbmode == 2 else 0)

      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["bframes"],
          variant["bitrate"], variant.get("fps", 30), profile
        ]

def gen_avc_cbr_parameters(spec, profiles, strapi=False):
  keys = ("case", "gop", "slices", "bframes", "bitrate", "fps", "profile")
  params = gen_avc_cbr_variants(spec, profiles, strapi)
  return keys, params

def gen_hevc_cbr_level_variants(spec, profiles, strapi=False):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("cbr_level", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["bframes"],
          variant["bitrate"], variant.get("fps", 30), profile, variant["level"]
        ]

def gen_hevc_cbr_level_parameters( spec, profiles):
  keys = ("case", "gop", "slices", "bframes", "bitrate", "fps", "profile", "level")
  params = gen_hevc_cbr_level_variants(spec, profiles)
  return keys, params

def gen_avc_vbr_variants(spec, profiles, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = copy.deepcopy(params.get("variants", dict()).get("vbr_strapi", []))
    else:
      variants = copy.deepcopy(params.get("variants", dict()).get("vbr", []))

    for variant in variants:
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["bframes"],
          variant["bitrate"], variant.get("fps", 30), variant.get("quality", 4),
          variant.get("refs", 1), profile
        ]

def gen_avc_vbr_parameters(spec, profiles, strapi=False):
  keys = ("case", "gop", "slices", "bframes", "bitrate", "fps", "quality", "refs", "profile")
  params = gen_avc_vbr_variants(spec, profiles, strapi)
  return keys, params

def gen_avc_cqp_lp_variants(spec, profiles, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = copy.deepcopy(params.get("variants", dict()).get("cqp_lp_strapi", []))
    else:
      variants = copy.deepcopy(params.get("variants", dict()).get("cqp_lp", []))

    for variant in variants:
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["bframes"], variant["qp"],
          variant["quality"], profile
        ]

def gen_avc_cqp_lp_parameters(spec, profiles, strapi=False):
  keys = ("case", "gop", "slices", "bframes", "qp", "quality", "profile")
  params = gen_avc_cqp_lp_variants(spec, profiles, strapi)
  return keys, params

def gen_avc_cbr_lp_variants(spec, profiles, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = copy.deepcopy(params.get("variants", dict()).get("cbr_lp_strapi", []))
    else:
      variants = copy.deepcopy(params.get("variants", dict()).get("cbr_lp", []))

    for variant in variants:
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["bframes"],
          variant["bitrate"], variant.get("fps", 30), profile
        ]

def gen_avc_cbr_lp_parameters(spec, profiles, strapi=False):
  keys = ("case", "gop", "slices", "bframes", "bitrate", "fps", "profile")
  params = gen_avc_cbr_lp_variants(spec, profiles, strapi)
  return keys, params

def gen_avc_vbr_lp_variants(spec, profiles, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = copy.deepcopy(params.get("variants", dict()).get("vbr_lp_strapi", []))
    else:
      variants = copy.deepcopy(params.get("variants", dict()).get("vbr_lp", []))

    for variant in variants:
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["bframes"],
          variant["bitrate"], variant.get("fps", 30), variant.get("quality", 4),
          variant.get("refs", 1), profile
        ]

def gen_avc_vbr_lp_parameters(spec, profiles, strapi=False):
  keys = ("case", "gop", "slices", "bframes", "bitrate", "fps", "quality", "refs", "profile")
  params = gen_avc_vbr_lp_variants(spec, profiles, strapi)
  return keys, params

def gen_avc_tcbrc_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("tcbrc", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [case, variant["bitrate"], variant.get("fps", 30), profile]

def gen_avc_tcbrc_parameters(spec, profiles):
  keys = ("case", "bitrate", "fps", "profile")
  params = gen_avc_tcbrc_variants(spec, profiles)
  return keys, params

def gen_avc_vbr_la_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("vbr_la", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["bframes"], variant["bitrate"], variant.get("fps", 30),
          variant.get("quality", 4), variant.get("refs", 1),
          profile, variant["ladepth"]
        ]

def gen_avc_vbr_la_parameters(spec, profiles):
  keys = ("case", "bframes", "bitrate", "fps", "quality", "refs", "profile", "ladepth")
  params = gen_avc_vbr_la_variants(spec, profiles)
  return keys, params

def gen_avc_forced_idr_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("forced_idr", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      rcmode  = variant["rcmode"]
      bitrate = variant.get("bitrate", None)
      qp      = variant.get("qp", None)
      if "cqp" == rcmode:
        assert bitrate == None, "We shouldn't set a value to bitrate for CQP."
        variant.update(maxrate = None)
      else:
        assert qp == None, "We shouldn't set a value to qp for CBR/VBR."
        if "cbr" == rcmode:
          variant.update(maxrate = bitrate)
        elif "vbr" == rcmode:
          variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, rcmode, bitrate, variant["maxrate"],
          qp, variant["quality"], profile
        ]

def gen_avc_forced_idr_parameters(spec, profiles):
  keys = ("case", "rcmode", "bitrate", "maxrate", "qp", "quality", "profile")
  params = gen_avc_forced_idr_variants(spec, profiles)
  return keys, params

def gen_avc_intref_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("intref", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      gop     = variant.get("gop", None)
      bframes = variant.get("bframes", None)
      bitrate = variant.get("bitrate", None)
      qp      = variant.get("qp", None)
      rcmode  = variant["rcmode"]
      reftype = variant.get("reftype", None)
      refsize = variant.get("refsize", None)
      refdist = variant.get("refdist", None)
      if "cqp" == rcmode:
        assert bitrate == None, "We shouldn't set a value to bitrate for CQP."
        variant.update(maxrate = None)
      else:
        assert qp == None, "We shouldn't set a value to qp for CBR/VBR."
        if "cbr" == rcmode:
          variant.update(maxrate = bitrate)
        elif "vbr" == rcmode:
          variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, gop, bframes, bitrate, qp, variant["maxrate"],
          profile, rcmode, reftype, refsize, refdist,
        ]

def gen_avc_intref_parameters(spec, profiles):
  keys = ("case", "gop", "bframes", "bitrate", "qp", "maxrate", "profile", "rcmode", "reftype", "refsize", "refdist")
  params = gen_avc_intref_variants(spec, profiles)
  return keys, params

def gen_avc_intref_lp_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("intref_lp", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      gop     = variant.get("gop", None)
      bframes = variant.get("bframes", None)
      bitrate = variant.get("bitrate", None)
      qp      = variant.get("qp", None)
      rcmode  = variant["rcmode"]
      reftype = variant.get("reftype", None)
      refsize = variant.get("refsize", None)
      refdist = variant.get("refdist", None)
      if "cqp" == rcmode:
        assert bitrate == None, "We shouldn't set a value to bitrate for CQP."
        variant.update(maxrate = None)
      else:
        assert qp == None, "We shouldn't set a value to qp for CBR/VBR."
        if "cbr" == rcmode:
          variant.update(maxrate = bitrate)
        elif "vbr" == rcmode:
          variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, gop, bframes, bitrate, qp, variant["maxrate"],
          profile, rcmode, reftype, refsize, refdist,
        ]

def gen_avc_intref_lp_parameters(spec, profiles):
  keys = ("case", "gop", "bframes", "bitrate", "qp", "maxrate", "profile", "rcmode", "reftype", "refsize", "refdist")
  params = gen_avc_intref_lp_variants(spec, profiles)
  return keys, params

def gen_avc_max_frame_size_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("max_frame_size", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      bitrate_max_frame_size = variant["bitrate_max_frame_size"]
      bitrate = bitrate_max_frame_size[0]
      maxframesize = bitrate_max_frame_size[1]
      variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, bitrate, variant["maxrate"],
          variant["fps"], maxframesize, profile
        ]

def gen_avc_max_frame_size_parameters(spec, profiles):
  keys = ("case", "bitrate", "maxrate", "fps", "maxframesize", "profile")
  params = gen_avc_max_frame_size_variants(spec, profiles)
  return keys, params

def gen_avc_roi_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("roi", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      gop     = variant.get("gop", None)
      bframes = variant.get("bframes", None)
      bitrate = variant.get("bitrate", None)
      rcmode  = variant["rcmode"]
      if "cbr" == rcmode:
        variant.update(maxrate = bitrate)
      elif "vbr" == rcmode:
        variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, gop, bframes, bitrate, variant["maxrate"],
          profile, rcmode,
        ]

def gen_avc_roi_parameters(spec, profiles):
  keys = ("case", "gop", "bframes", "bitrate", "maxrate", "profile", "rcmode")
  params = gen_avc_roi_variants(spec, profiles)
  return keys, params

def gen_avc_roi_lp_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("roi_lp", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      gop     = variant.get("gop", None)
      bframes = variant.get("bframes", None)
      bitrate = variant.get("bitrate", None)
      rcmode  = variant["rcmode"]
      if "cbr" == rcmode:
        variant.update(maxrate = bitrate)
      elif "vbr" == rcmode:
        variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, gop, bframes, bitrate, variant["maxrate"],
          profile, rcmode,
        ]

def gen_avc_roi_lp_parameters(spec, profiles):
  keys = ("case", "gop", "bframes", "bitrate", "maxrate", "profile", "rcmode")
  params = gen_avc_roi_lp_variants(spec, profiles)
  return keys, params

def gen_avc_rqp_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("rqp", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      gop     = variant.get("gop", None)
      bframes = variant.get("bframes", None)
      bitrate = variant.get("bitrate", None)
      rcmode  = variant["rcmode"]
      maxi    = variant.get("maxi", None)
      mini    = variant.get("mini", None)
      maxp    = variant.get("maxp", None)
      minp    = variant.get("minp", None)
      maxb    = variant.get("maxb", None)
      minb    = variant.get("minb", None)
      if "cbr" == rcmode:
        variant.update(maxrate = bitrate)
      elif "vbr" == rcmode:
        variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, gop, bframes, bitrate, variant["maxrate"],
          profile, rcmode, maxi, mini, maxp, minp, maxb, minb,
        ]

def gen_avc_rqp_parameters(spec, profiles):
  keys = ("case", "gop", "bframes", "bitrate", "maxrate", "profile", "rcmode", "maxi", "mini", "maxp", "minp", "maxb", "minb")
  params = gen_avc_rqp_variants(spec, profiles)
  return keys, params

def gen_hevc_cqp_lp_variants(spec, profiles, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = copy.deepcopy(params.get("variants", dict()).get("cqp_lp_strapi", []))
    else:
      variants = copy.deepcopy(params.get("variants", dict()).get("cqp_lp", []))

    for variant in variants:
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["qp"],
          variant["quality"], profile
        ]

def gen_hevc_cqp_lp_parameters(spec, profiles, strapi=False):
  keys = ("case", "gop", "slices", "qp", "quality", "profile")
  params = gen_hevc_cqp_lp_variants(spec, profiles, strapi)
  return keys, params

def gen_hevc_cbr_lp_variants(spec, profiles, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = copy.deepcopy(params.get("variants", dict()).get("cbr_lp_strapi", []))
    else:
      variants = copy.deepcopy(params.get("variants", dict()).get("cbr_lp", []))

    for variant in variants:
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"],
          variant["bitrate"], variant.get("fps", 30), profile
        ]

def gen_hevc_cbr_lp_parameters(spec, profiles, strapi=False):
  keys = ("case", "gop", "slices", "bitrate", "fps", "profile")
  params = gen_hevc_cbr_lp_variants(spec, profiles, strapi)
  return keys, params

def gen_hevc_vbr_lp_variants(spec, profiles, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = copy.deepcopy(params.get("variants", dict()).get("vbr_lp_strapi", []))
    else:
      variants = copy.deepcopy(params.get("variants", dict()).get("vbr_lp", []))

    for variant in variants:
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"],
          variant["bitrate"], variant.get("fps", 30), variant.get("quality", 4),
          variant.get("refs", 1), profile
        ]

def gen_hevc_vbr_lp_parameters(spec, profiles, strapi=False):
  keys = ("case", "gop", "slices", "bitrate", "fps", "quality", "refs", "profile")
  params = gen_hevc_vbr_lp_variants(spec, profiles, strapi)
  return keys, params

def gen_hevc_qvbr_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("qvbr", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"],
          variant["bitrate"], variant.get("qp", 28), variant.get("fps", 30), variant.get("quality", 4),
          variant.get("refs", 1), profile
        ]

def gen_hevc_qvbr_parameters(spec, profiles):
  keys = ("case", "gop", "slices", "bitrate", "qp", "fps", "quality", "refs", "profile")
  params = gen_hevc_qvbr_variants(spec, profiles)
  return keys, params

def gen_hevc_qvbr_lp_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("qvbr_lp", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"],
          variant["bitrate"], variant.get("qp", 28), variant.get("fps", 30), variant.get("quality", 4),
          variant.get("refs", 1), profile
        ]

def gen_hevc_qvbr_lp_parameters(spec, profiles):
  keys = ("case", "gop", "slices", "bitrate", "qp", "fps", "quality", "refs", "profile")
  params = gen_hevc_qvbr_lp_variants(spec, profiles)
  return keys, params

def gen_hevc_pict_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("pict", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      gop     = variant.get("gop", None)
      bframes = variant.get("bframes", None)
      bitrate = variant.get("bitrate", None)
      qp      = variant.get("qp", None)
      rcmode  = variant["rcmode"]
      if "cqp" == rcmode:
        assert bitrate == None, "We shouldn't set a value to bitrate for CQP."
        variant.update(maxrate = None)
      else:
        assert qp == None, "We shouldn't set a value to qp for CBR/VBR."
        if "cbr" == rcmode:
          variant.update(maxrate = bitrate)
        elif "vbr" == rcmode:
          variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, gop, bframes, bitrate, qp, variant["maxrate"],
          profile, rcmode,
        ]

def gen_hevc_pict_parameters(spec, profiles):
  keys = ("case", "gop", "bframes", "bitrate", "qp", "maxrate", "profile", "rcmode")
  params = gen_hevc_pict_variants(spec, profiles)
  return keys, params

def gen_hevc_pict_lp_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("pict_lp", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      gop     = variant.get("gop", None)
      bframes = variant.get("bframes", None)
      bitrate = variant.get("bitrate", None)
      qp      = variant.get("qp", None)
      rcmode  = variant["rcmode"]
      if "cqp" == rcmode:
        assert bitrate == None, "We shouldn't set a value to bitrate for CQP."
        variant.update(maxrate = None)
      else:
        assert qp == None, "We shouldn't set a value to qp for CBR/VBR."
        if "cbr" == rcmode:
          variant.update(maxrate = bitrate)
        elif "vbr" == rcmode:
          variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, gop, bframes, bitrate, qp, variant["maxrate"],
          profile, rcmode,
        ]

def gen_hevc_pict_lp_parameters(spec, profiles):
  keys = ("case", "gop", "bframes", "bitrate", "qp", "maxrate", "profile", "rcmode")
  params = gen_hevc_pict_lp_variants(spec, profiles)
  return keys, params

def gen_hevc_seek_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("seek", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      gop     = variant.get("gop", None)
      bframes = variant.get("bframes", None)
      bitrate = variant.get("bitrate", None)
      qp      = variant.get("qp", None)
      fps     = variant.get("fps", 25)
      rcmode  = variant["rcmode"]
      seek    = variant["seek"]
      if "cqp" == rcmode:
        assert bitrate == None, "We shouldn't set a value to bitrate for CQP."
        variant.update(maxrate = None)
      else:
        assert qp == None, "We shouldn't set a value to qp for CBR/VBR."
        if "cbr" == rcmode:
          variant.update(maxrate = bitrate)
        elif "vbr" == rcmode:
          variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, gop, bframes, bitrate, qp, variant["maxrate"],
          profile, rcmode, seek, fps,
        ]

def gen_hevc_seek_parameters(spec, profiles):
  keys = ("case", "gop", "bframes", "bitrate", "qp", "maxrate", "profile", "rcmode", "seek", "fps")
  params = gen_hevc_seek_variants(spec, profiles)
  return keys, params

def gen_hevc_seek_lp_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("seek_lp", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      gop     = variant.get("gop", None)
      bframes = variant.get("bframes", None)
      bitrate = variant.get("bitrate", None)
      qp      = variant.get("qp", None)
      fps     = variant.get("fps", 25)
      rcmode  = variant["rcmode"]
      seek    = variant["seek"]
      if "cqp" == rcmode:
        assert bitrate == None, "We shouldn't set a value to bitrate for CQP."
        variant.update(maxrate = None)
      else:
        assert qp == None, "We shouldn't set a value to qp for CBR/VBR."
        if "cbr" == rcmode:
          variant.update(maxrate = bitrate)
        elif "vbr" == rcmode:
          variant.update(maxrate = bitrate * 2)
      for profile in cprofiles:
        yield [
          case, gop, bframes, bitrate, qp, variant["maxrate"],
          profile, rcmode, seek, fps,
        ]

def gen_hevc_seek_lp_parameters(spec, profiles):
  keys = ("case", "gop", "bframes", "bitrate", "qp", "maxrate", "profile", "rcmode", "seek", "fps")
  params = gen_hevc_seek_lp_variants(spec, profiles)
  return keys, params

gen_hevc_cqp_parameters = gen_avc_cqp_parameters
gen_hevc_cbr_parameters = gen_avc_cbr_parameters
gen_hevc_vbr_parameters = gen_avc_vbr_parameters
gen_hevc_bdepth_parameters = gen_avc_bdepth_parameters
gen_hevc_bdepth_lp_parameters = gen_avc_bdepth_lp_parameters
gen_hevc_roi_parameters = gen_avc_roi_parameters
gen_hevc_roi_lp_parameters = gen_avc_roi_lp_parameters
gen_hevc_forced_idr_parameters = gen_avc_forced_idr_parameters
gen_hevc_intref_lp_parameters = gen_avc_intref_lp_parameters
gen_hevc_max_frame_size_parameters = gen_avc_max_frame_size_parameters
gen_hevc_tcbrc_parameters = gen_avc_tcbrc_parameters

def gen_mpeg2_cqp_variants(spec):
  for case, params in spec.items():
    variants = copy.deepcopy(params.get("variants", dict()).get("cqp", None))
    if variants is None:
      keys = ["gop", "bframes", "qp", "quality"]
      product  = list(itertools.product([1], [0], [14, 28], [1, 4, 7]))  # I
      product += list(itertools.product([30], [0], [14, 28], [1, 4, 7])) # IP
      product += list(itertools.product([30], [2], [14, 28], [1, 4, 7])) # IPB
      variants = [dict(zip(keys, vals)) for vals in product]

    for variant in variants:
      # backwards compatibility for ipbmode user config
      ipbmode = variant.get("ipbmode", None)
      if ipbmode is not None:
        assert not variant.get("gop", None)
        assert not variant.get("bframes", None)
        variant.update(
          gop = 30 if ipbmode != 0 else 1,
          bframes = 2 if ipbmode == 2 else 0)

      yield [
        case, variant["gop"], variant["bframes"],
        variant["qp"], variant["quality"]
      ]

def gen_mpeg2_cqp_parameters(spec):
  keys = ("case", "gop", "bframes", "qp", "quality")
  params = gen_mpeg2_cqp_variants(spec)
  return keys, params

def gen_jpeg_cqp_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("cqp", None)

    if variants is None:
      variants = list()
      for quality in [10, 25, 50, 75, 100]:
        variants.append(dict(quality = quality))

    for variant in variants:
      yield [case, variant["quality"]]

def gen_jpeg_cqp_parameters(spec):
  keys = ("case", "quality")
  params = gen_jpeg_cqp_variants(spec)
  return keys, params

def gen_vp8_cqp_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("cqp", None)

    if variants is None:
      keys = ["ipmode", "qp", "quality", "looplvl", "loopshp"]
      product = itertools.product([0, 1], [14, 28], [1, 4, 7], [0, 16, 63], [0, 4, 7])
      variants = [dict(zip(keys, vals)) for vals in product]

    for variant in variants:
      yield [
        case, variant["ipmode"], variant["qp"], variant["quality"],
        variant["looplvl"], variant["loopshp"]]

def gen_vp8_cqp_parameters(spec):
  keys = ("case", "ipmode", "qp", "quality", "looplvl", "loopshp")
  params = gen_vp8_cqp_variants(spec)
  return keys, params

def gen_vp8_cbr_variants(spec):
  for case, params in spec.items():
    for variant in params.get("variants", dict()).get("cbr", []):
        # Required: bitrate
        # Optional: gop, fps, looplvl, loopshp
        yield [
          case, variant.get("gop", 30), variant["bitrate"],
          variant.get("fps", 30), variant.get("looplvl", 0),
          variant.get("loopshp", 0),
        ]

def gen_vp8_cbr_parameters(spec):
  keys = ("case", "gop", "bitrate", "fps", "looplvl", "loopshp")
  params = gen_vp8_cbr_variants(spec)
  return keys, params

def gen_vp8_vbr_variants(spec):
  for case, params in spec.items():
    for variant in params.get("variants", dict()).get("vbr", []):
        # Required: bitrate
        # Optional: gop, fps, quality, looplvl, loopshp
        yield [
          case, variant.get("gop", 30), variant["bitrate"],
          variant.get("fps", 30), variant.get("quality", 4),
          variant.get("looplvl", 0), variant.get("loopshp", 0),
        ]

def gen_vp8_vbr_parameters(spec):
  keys = ("case", "gop", "bitrate", "fps", "quality", "looplvl", "loopshp")
  params = gen_vp8_vbr_variants(spec)
  return keys, params

def gen_vp9_cqp_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("cqp", None)

    if variants is None:
      keys = ["ipmode", "qp", "quality", "slices", "refmode", "looplvl", "loopshp"]
      product = itertools.product([0, 1], [14, 28], [1, 4, 7], [1, 3], [0, 1], [0, 16, 63], [0, 4, 7])
      variants = [dict(zip(keys, vals)) for vals in product]

    for variant in variants:
      yield [
        case, variant["ipmode"], variant["qp"], variant["quality"], variant.get("slices", 1),
        variant["refmode"], variant["looplvl"], variant["loopshp"]]

def gen_vp9_cqp_parameters(spec):
  keys = ("case", "ipmode", "qp", "quality", "slices", "refmode", "looplvl", "loopshp")
  params = gen_vp9_cqp_variants(spec)
  return keys, params

def gen_vp9_cbr_variants(spec):
  for case, params in spec.items():
    for variant in params.get("variants", dict()).get("cbr", []):
        # Required: bitrate
        # Optional: gop, fps, refmode, looplvl, loopshp
        yield [
          case, variant.get("gop", 30), variant["bitrate"],
          variant.get("fps", 30), variant.get("slices", 1), variant.get("refmode", 0),
          variant.get("looplvl", 0), variant.get("loopshp", 0),
        ]

def gen_vp9_cbr_parameters(spec):
  keys = ("case", "gop", "bitrate", "fps", "slices", "refmode", "looplvl", "loopshp")
  params = gen_vp9_cbr_variants(spec)
  return keys, params

def gen_vp9_vbr_variants(spec):
  for case, params in spec.items():
    for variant in params.get("variants", dict()).get("vbr", []):
        # Required: bitrate
        # Optional: gop, fps, refmode, quality, looplvl, loopshp
        yield [
          case, variant.get("gop", 30), variant["bitrate"],
          variant.get("fps", 30), variant.get("slices", 1), variant.get("refmode", 0),
          variant.get("quality", 4), variant.get("looplvl", 0),
          variant.get("loopshp", 0),
        ]

def gen_vp9_vbr_parameters(spec):
  keys = ("case", "gop", "bitrate", "fps", "slices", "refmode", "quality", "looplvl", "loopshp")
  params = gen_vp9_vbr_variants(spec)
  return keys, params

def gen_vp9_seek_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("seek", [])
    for variant in variants:
        rcmode = variant["rcmode"]
        bitrate = variant["bitrate"]

        # Update maxrate according to rcmode
        if "cbr" == rcmode:
          variant.update(maxrate = bitrate)
        elif "vbr" == rcmode:
          variant.update(maxrate = bitrate * 2)
        else:
          variant.update(maxrate = None)

        yield [
            case, rcmode, bitrate, variant.get("maxrate", None),
            variant.get("fps", 25), variant.get("seek", 1)
            ]

def gen_vp9_seek_parameters(spec):
  keys = ("case", "rcmode", "bitrate", "maxrate", "fps", "seek")
  params = gen_vp9_seek_variants(spec)
  return keys, params

def gen_vp9_cqp_lp_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("cqp_lp", [])
    for variant in variants:
      yield [
        case, variant["ipmode"], variant["qp"], variant["quality"], variant["slices"],
        variant["refmode"], variant["looplvl"], variant["loopshp"]]

def gen_vp9_cqp_lp_parameters(spec):
  keys = ("case", "ipmode", "qp", "quality", "slices", "refmode", "looplvl", "loopshp")
  params = gen_vp9_cqp_lp_variants(spec)
  return keys, params

def gen_vp9_cbr_lp_variants(spec):
  for case, params in spec.items():
    for variant in params.get("variants", dict()).get("cbr_lp", []):
        # Required: bitrate
        # Optional: gop, fps, refmode, looplvl, loopshp
        yield [
          case, variant["gop"], variant["bitrate"], variant.get("fps", 30),
          variant["slices"], variant.get("refmode", 0),
          variant.get("looplvl", 0), variant.get("loopshp", 0),
        ]

def gen_vp9_cbr_lp_parameters(spec):
  keys = ("case", "gop", "bitrate", "fps", "slices", "refmode", "looplvl", "loopshp")
  params = gen_vp9_cbr_lp_variants(spec)
  return keys, params

def gen_vp9_vbr_lp_variants(spec):
  for case, params in spec.items():
    for variant in params.get("variants", dict()).get("vbr_lp", []):
        # Required: bitrate
        # Optional: gop, fps, refmode, looplvl, loopshp
        yield [
          case, variant["gop"], variant["bitrate"], variant.get("fps", 30),
          variant["slices"], variant["quality"], variant.get("refmode", 0),
          variant.get("looplvl", 0), variant.get("loopshp", 0),
        ]

def gen_vp9_vbr_lp_parameters(spec):
  keys = ("case", "gop", "bitrate", "fps", "slices", "quality", "refmode", "looplvl", "loopshp")
  params = gen_vp9_vbr_lp_variants(spec)
  return keys, params

def gen_vp9_seek_lp_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("seek_lp", [])
    for variant in variants:
        rcmode = variant["rcmode"]
        bitrate = variant["bitrate"]

        # Update maxrate according to rcmode
        if "cbr" == rcmode:
          variant.update(maxrate = bitrate)
        elif "vbr" == rcmode:
          variant.update(maxrate = bitrate * 2)
        else:
          variant.update(maxrate = None)

        yield [
            case, rcmode, bitrate, variant.get("maxrate", None),
            variant.get("fps", 25), variant.get("seek", 1)
            ]

def gen_vp9_seek_lp_parameters(spec):
  keys = ("case", "rcmode", "bitrate", "maxrate", "fps", "seek")
  params = gen_vp9_seek_lp_variants(spec)
  return keys, params

gen_avc_seek_parameters = gen_vp9_seek_parameters
gen_avc_seek_lp_parameters = gen_vp9_seek_lp_parameters

def gen_av1_cqp_variants(spec, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = params.get("variants", dict()).get("cqp_strapi", [])
    else:
      variants = params.get("variants", dict()).get("cqp", [])

    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["qp"], variant["quality"],
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("profile", "profile0")]

def gen_av1_cqp_parameters(spec, strapi=False):
  keys = ("case", "gop", "bframes", "qp", "quality", "tilecols", "tilerows", "profile")
  params = gen_av1_cqp_variants(spec, strapi)
  return keys, params

def gen_av1_icq_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("icq", [])
    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["qp"], variant["quality"],
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("profile", "profile0")]

def gen_av1_icq_parameters(spec):
  keys = ("case", "gop", "bframes", "qp", "quality", "tilecols", "tilerows", "profile")
  params = gen_av1_icq_variants(spec)
  return keys, params

def gen_av1_icq_lp_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("icq_lp", [])
    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["qp"], variant["quality"],
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("profile", "profile0")]

def gen_av1_icq_lp_parameters(spec):
  keys = ("case", "gop", "bframes", "qp", "quality", "tilecols", "tilerows", "profile")
  params = gen_av1_icq_lp_variants(spec)
  return keys, params

def gen_av1_cbr_variants(spec, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = params.get("variants", dict()).get("cbr_strapi", [])
    else:
      variants = params.get("variants", dict()).get("cbr", [])

    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["bitrate"], variant.get("quality", 4),
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("fps", 30),
        variant.get("profile", "profile0")]

def gen_av1_cbr_parameters(spec, strapi=False):
  keys = ("case", "gop", "bframes", "bitrate", "quality", "tilecols", "tilerows", "fps", "profile")
  params = gen_av1_cbr_variants(spec, strapi)
  return keys, params

def gen_av1_vbr_variants(spec, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = params.get("variants", dict()).get("vbr_strapi", [])
    else:
      variants = params.get("variants", dict()).get("vbr", [])

    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["bitrate"], variant.get("quality", 4),
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("fps", 30),
        variant.get("profile", "profile0")]

def gen_av1_vbr_parameters(spec, strapi=False):
  keys = ("case", "gop", "bframes", "bitrate", "quality", "tilecols", "tilerows", "fps", "profile")
  params = gen_av1_vbr_variants(spec, strapi)
  return keys, params

def gen_av1_cqp_lp_variants(spec, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = params.get("variants", dict()).get("cqp_lp_strapi", [])
    else:
      variants = params.get("variants", dict()).get("cqp_lp", [])

    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["qp"], variant["quality"],
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("profile", "profile0")]

def gen_av1_cqp_lp_parameters(spec, strapi=False):
  keys = ("case", "gop", "bframes", "qp", "quality", "tilecols", "tilerows", "profile")
  params = gen_av1_cqp_lp_variants(spec, strapi)
  return keys, params

def gen_av1_cbr_lp_variants(spec, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = params.get("variants", dict()).get("cbr_lp_strapi", [])
    else:
      variants = params.get("variants", dict()).get("cbr_lp", [])

    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["bitrate"], variant.get("quality", 4),
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("fps", 30),
        variant.get("profile", "profile0")]

def gen_av1_cbr_lp_parameters(spec, strapi=False):
  keys = ("case", "gop", "bframes", "bitrate", "quality", "tilecols", "tilerows", "fps", "profile")
  params = gen_av1_cbr_lp_variants(spec, strapi)
  return keys, params

def gen_av1_vbr_lp_variants(spec, strapi=False):
  for case, params in spec.items():
    if strapi:
      variants = params.get("variants", dict()).get("vbr_lp_strapi", [])
    else:
      variants = params.get("variants", dict()).get("vbr_lp", [])

    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["bitrate"], variant.get("quality", 4),
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("fps", 30),
        variant.get("profile", "profile0")]

def gen_av1_vbr_lp_parameters(spec, strapi=False):
  keys = ("case", "gop", "bframes", "bitrate", "quality", "tilecols", "tilerows", "fps", "profile")
  params = gen_av1_vbr_lp_variants(spec, strapi)
  return keys, params

def gen_vpp_sharpen_variants(spec):
  for case, params in spec.items():
    variants = params.get("levels", None) or [0, 1, 20, 50, 59, 99, 100]
    for variant in set(variants):
      yield [case, variant]

def gen_vpp_sharpen_parameters(spec):
  keys = ("case", "level")
  params = gen_vpp_sharpen_variants(spec)
  return keys, params

gen_vpp_denoise_parameters = gen_vpp_sharpen_parameters
gen_vpp_brightness_parameters = gen_vpp_sharpen_parameters
gen_vpp_contrast_parameters = gen_vpp_sharpen_parameters
gen_vpp_hue_parameters = gen_vpp_sharpen_parameters
gen_vpp_saturation_parameters = gen_vpp_sharpen_parameters

def gen_vpp_deinterlace_variants(spec, default_modes):
  for case, params in spec.items():
    # Keeps track of variants (modes) that we've already yielded for this
    # case so we don't produce duplicates.
    seen = set()

    # Use the modes from the user spec/config if it's defined.  Otherwise, use
    # the modes provided by the default_modes.
    modes = params.get("modes", default_modes)

    # For each specified mode, generate and yield each variant for this case
    for mode in modes:
      method = mode.get("method", None)
      rate = mode.get("rate", None)

      if method is None: # method is variant, rate is fixed
        assert rate is not None, "user config must specify method and/or rate"
        # select all modes from the default_modes that match the specified rate.
        gmodes = filter(lambda m: m["rate"] == rate, default_modes)
      elif rate is None: # rate is variant, method is fixed
        assert method is not None, "user config must specify method and/or rate"
        # select all modes from the default_modes that match the specified method.
        gmodes = filter(lambda m: m["method"] == method, default_modes)
      else: # rate and method are fixed
        gmodes = [mode]

      # For each generated mode, yield a unique variant for this case
      for gmode in gmodes:
        mode_hash = tuple(sorted(gmode.values()))
        # only yield if we haven't seen this mode for this case
        if mode_hash not in seen:
          yield [case, gmode["method"], gmode["rate"]]
          seen.add(mode_hash)

def gen_vpp_deinterlace_parameters(spec, default_modes):
  keys = ("case", "method", "rate")
  params = gen_vpp_deinterlace_variants(spec, default_modes)
  return keys, params

def gen_vpp_csc_variants(spec):
  for case, params in spec.items():
    variants = params.get("colorspaces", None) or ["NV12", "YV12", "I420"]
    for variant in set(variants):
      yield [case, variant]

def gen_vpp_csc_parameters(spec):
  keys = ("case", "csc")
  params = gen_vpp_csc_variants(spec)
  return keys, params

def gen_vpp_scale_variants(spec):
  for case, params in spec.items():
    variants = params.get("scale_resolutions", None) or []
    for scale_width, scale_height in variants:
      yield [case, scale_width, scale_height]

def gen_vpp_scale_parameters(spec):
  keys = ("case", "scale_width", "scale_height")
  params = gen_vpp_scale_variants(spec)
  return keys, params

def gen_vpp_mirroring_variants(spec):
  for case, params in spec.items():
    variants = params.get("methods", None) or ["vertical", "horizontal"]
    for variant in variants:
      yield [case, variant]

def gen_vpp_mirroring_parameters(spec):
  keys = ("case", "method")
  params = gen_vpp_mirroring_variants(spec)
  return keys, params

def gen_vpp_rotation_variants(spec):
  for case, params in spec.items():
    variants = params.get("rotations", None) or [0, 90, 180, 270]
    for variant in variants:
      yield [case, variant]

def gen_vpp_rotation_parameters(spec):
  keys = ("case", "degrees")
  params = gen_vpp_rotation_variants(spec)
  return keys, params

def gen_vpp_transpose_variants(spec):
  for case, params in spec.items():
    variants = params.get("transpose", None) or []
    for degrees, method in variants:
      yield [case, degrees, method]

def gen_vpp_transpose_parameters(spec):
  keys = ("case", "degrees", "method")
  params = gen_vpp_transpose_variants(spec)
  return keys, params

def gen_vpp_crop_variants(spec):
  for case, params in spec.items():
    variants = params.get("crop", [])
    for variant in variants:
      yield [
        case, variant.get("left", 0), variant.get("right", 0),
        variant.get("top", 0), variant.get("bottom", 0)
      ]

def gen_vpp_crop_parameters(spec):
  keys = ("case", "left", "right", "top", "bottom")
  params = gen_vpp_crop_variants(spec)
  return keys, params

def gen_vpp_hvstack_variants(spec, mode):
  for case, params in spec.items():
    variants = filter(lambda s: mode == s["mode"], params.get("stacks", []))
    for variant in variants:
      yield [case, variant["inputs"]]

def gen_vpp_hstack_parameters(spec):
  keys = ("case", "inputs")
  params = gen_vpp_hvstack_variants(spec, "hstack")
  return keys, params

def gen_vpp_vstack_parameters(spec):
  keys = ("case", "inputs")
  params = gen_vpp_hvstack_variants(spec, "vstack")
  return keys, params

def gen_vpp_xstack_variants(spec):
  for case, params in spec.items():
    variants = filter(lambda s: "xstack" == s["mode"], params.get("stacks", []))
    for variant in variants:
      yield [
        case, variant["rows"], variant["cols"],
        variant["tilew"], variant["tileh"],
      ]

def gen_vpp_xstack_parameters(spec):
  keys = ("case", "rows", "cols", "tilew", "tileh")
  params = gen_vpp_xstack_variants(spec)
  return keys, params

def gen_vpp_h2s_variants(spec):
  for case, params in spec.items():
    variants = filter(lambda s: "h2s" == s["mode"], params.get("tonemap", []))
    for variant in variants:
      yield [
        case, variant["csc"]
      ]

def gen_vpp_h2s_parameters(spec):
  keys = ("case", "csc")
  params = gen_vpp_h2s_variants(spec)
  return keys, params

def gen_vpp_overlay_variants(spec):
  for case, params in spec.items():
    alphas = params.get("alphas", [])
    for alpha in alphas:
        yield [case, alpha]

def gen_vpp_overlay_parameters(spec):
  keys = ("case", "alpha")
  params = gen_vpp_overlay_variants(spec)
  return keys, params

def gen_vpp_color_range_variants(spec):
  for case, params in spec.items():
    ranges = params.get("ranges", [])
    for rng in ranges:
        yield [case, rng]

def gen_vpp_color_range_parameters(spec):
  keys = ("case", "rng")
  params = gen_vpp_color_range_variants(spec)
  return keys, params
