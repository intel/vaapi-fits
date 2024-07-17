###
### Copyright (C) 2024 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import copy
import itertools

def gen_avc_cqp_strapi_variants(spec, profiles):
  for case, params in spec.items():
    variants = copy.deepcopy(params.get("variants", dict()).get("cqp_strapi", None))
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

def gen_avc_cqp_strapi_parameters(spec, profiles):
  keys = ("case", "gop", "slices", "bframes", "qp", "quality", "profile")
  params = gen_avc_cqp_strapi_variants(spec, profiles)
  return keys, params

def gen_avc_cbr_strapi_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("cbr_strapi", [])):
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

def gen_avc_cbr_strapi_parameters(spec, profiles):
  keys = ("case", "gop", "slices", "bframes", "bitrate", "fps", "profile")
  params = gen_avc_cbr_strapi_variants(spec, profiles)
  return keys, params

def gen_avc_vbr_strapi_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("vbr_strapi", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["bframes"],
          variant["bitrate"], variant.get("fps", 30), variant.get("quality", 4),
          variant.get("refs", 1), profile
        ]

def gen_avc_vbr_strapi_parameters(spec, profiles):
  keys = ("case", "gop", "slices", "bframes", "bitrate", "fps", "quality", "refs", "profile")
  params = gen_avc_vbr_strapi_variants(spec, profiles)
  return keys, params

def gen_avc_cqp_lp_strapi_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("cqp_lp_strapi", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["bframes"], variant["qp"],
          variant["quality"], profile
        ]

def gen_avc_cqp_lp_strapi_parameters(spec, profiles):
  keys = ("case", "gop", "slices", "bframes", "qp", "quality", "profile")
  params = gen_avc_cqp_lp_strapi_variants(spec, profiles)
  return keys, params

def gen_avc_cbr_lp_strapi_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("cbr_lp_strapi", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["bframes"],
          variant["bitrate"], variant.get("fps", 30), profile
        ]

def gen_avc_cbr_lp_strapi_parameters(spec, profiles):
  keys = ("case", "gop", "slices", "bframes", "bitrate", "fps", "profile")
  params = gen_avc_cbr_lp_strapi_variants(spec, profiles)
  return keys, params

def gen_avc_vbr_lp_strapi_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("vbr_lp_strapi", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["bframes"],
          variant["bitrate"], variant.get("fps", 30), variant.get("quality", 4),
          variant.get("refs", 1), profile
        ]

def gen_avc_vbr_lp_strapi_parameters(spec, profiles):
  keys = ("case", "gop", "slices", "bframes", "bitrate", "fps", "quality", "refs", "profile")
  params = gen_avc_vbr_lp_strapi_variants(spec, profiles)
  return keys, params

def gen_hevc_cqp_lp_strapi_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("cqp_lp_strapi", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"], variant["qp"],
          variant["quality"], profile
        ]

def gen_hevc_cqp_lp_strapi_parameters(spec, profiles):
  keys = ("case", "gop", "slices", "qp", "quality", "profile")
  params = gen_hevc_cqp_lp_strapi_variants(spec, profiles)
  return keys, params

def gen_hevc_cbr_lp_strapi_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("cbr_lp_strapi", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"],
          variant["bitrate"], variant.get("fps", 30), profile
        ]

def gen_hevc_cbr_lp_strapi_parameters(spec, profiles):
  keys = ("case", "gop", "slices", "bitrate", "fps", "profile")
  params = gen_hevc_cbr_lp_strapi_variants(spec, profiles)
  return keys, params

def gen_hevc_vbr_lp_strapi_variants(spec, profiles):
  for case, params in spec.items():
    for variant in copy.deepcopy(params.get("variants", dict()).get("vbr_lp_strapi", [])):
      uprofile = variant.get("profile", None)
      cprofiles = [uprofile] if uprofile else profiles
      for profile in cprofiles:
        yield [
          case, variant["gop"], variant["slices"],
          variant["bitrate"], variant.get("fps", 30), variant.get("quality", 4),
          variant.get("refs", 1), profile
        ]

def gen_hevc_vbr_lp_strapi_parameters(spec, profiles):
  keys = ("case", "gop", "slices", "bitrate", "fps", "quality", "refs", "profile")
  params = gen_hevc_vbr_lp_strapi_variants(spec, profiles)
  return keys, params

gen_hevc_cqp_strapi_parameters = gen_avc_cqp_strapi_parameters
gen_hevc_cbr_strapi_parameters = gen_avc_cbr_strapi_parameters
gen_hevc_vbr_strapi_parameters = gen_avc_vbr_strapi_parameters

def gen_av1_cqp_strapi_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("cqp_strapi", [])
    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["qp"], variant["quality"],
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("profile", "profile0")]

def gen_av1_cqp_strapi_parameters(spec):
  keys = ("case", "gop", "bframes", "qp", "quality", "tilecols", "tilerows", "profile")
  params = gen_av1_cqp_strapi_variants(spec)
  return keys, params

def gen_av1_cbr_strapi_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("cbr_strapi", [])
    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["bitrate"], variant.get("quality", 4),
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("fps", 30),
        variant.get("profile", "profile0")]

def gen_av1_cbr_strapi_parameters(spec):
  keys = ("case", "gop", "bframes", "bitrate", "quality", "tilecols", "tilerows", "fps", "profile")
  params = gen_av1_cbr_strapi_variants(spec)
  return keys, params

def gen_av1_vbr_strapi_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("vbr_strapi", [])
    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["bitrate"], variant.get("quality", 4),
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("fps", 30),
        variant.get("profile", "profile0")]

def gen_av1_vbr_strapi_parameters(spec):
  keys = ("case", "gop", "bframes", "bitrate", "quality", "tilecols", "tilerows", "fps", "profile")
  params = gen_av1_vbr_strapi_variants(spec)
  return keys, params

def gen_av1_cqp_lp_strapi_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("cqp_lp_strapi", [])
    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["qp"], variant["quality"],
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("profile", "profile0")]

def gen_av1_cqp_lp_strapi_parameters(spec):
  keys = ("case", "gop", "bframes", "qp", "quality", "tilecols", "tilerows", "profile")
  params = gen_av1_cqp_lp_strapi_variants(spec)
  return keys, params

def gen_av1_cbr_lp_strapi_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("cbr_lp_strapi", [])
    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["bitrate"], variant.get("quality", 4),
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("fps", 30),
        variant.get("profile", "profile0")]

def gen_av1_cbr_lp_strapi_parameters(spec):
  keys = ("case", "gop", "bframes", "bitrate", "quality", "tilecols", "tilerows", "fps", "profile")
  params = gen_av1_cbr_lp_strapi_variants(spec)
  return keys, params

def gen_av1_vbr_lp_strapi_variants(spec):
  for case, params in spec.items():
    variants = params.get("variants", dict()).get("vbr_lp_strapi", [])
    for variant in variants:
      yield [
        case, variant["gop"], variant["bframes"], variant["bitrate"], variant.get("quality", 4),
        variant.get("tilecols", 0), variant.get("tilerows", 0), variant.get("fps", 30),
        variant.get("profile", "profile0")]

def gen_av1_vbr_lp_strapi_parameters(spec):
  keys = ("case", "gop", "bframes", "bitrate", "quality", "tilecols", "tilerows", "fps", "profile")
  params = gen_av1_vbr_lp_strapi_variants(spec)
  return keys, params
