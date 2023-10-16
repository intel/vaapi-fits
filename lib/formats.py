###
### Copyright (C) 2019-2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import enum

@enum.unique
class Subsampling(str, enum.Enum):
  NONE    = "NONE"
  YUV400  = "YUV400"
  YUV420  = "YUV420"
  YUV422  = "YUV422"
  YUV444  = "YUV444"

@enum.unique
class PixelFormat(str, enum.Enum):
  def __new__(cls, value, ss = Subsampling.NONE, bitdepth = 0):
    obj = str.__new__(cls, value)
    obj._value_ = value
    obj.__subsampling = ss
    obj.__bitdepth = bitdepth
    return obj

  NONE  = "NONE"
  _Y800 = "Y800", Subsampling.YUV400,  8
  _I420 = "I420", Subsampling.YUV420,  8
  _NV12 = "NV12", Subsampling.YUV420,  8
  _YV12 = "YV12", Subsampling.YUV420,  8
  _P010 = "P010", Subsampling.YUV420, 10
  _I010 = "I010", Subsampling.YUV420, 10
  _P012 = "P012", Subsampling.YUV420, 12
  _422H = "422H", Subsampling.YUV422,  8
  _422V = "422V", Subsampling.YUV422,  8
  _YUY2 = "YUY2", Subsampling.YUV422,  8
  _Y210 = "Y210", Subsampling.YUV422, 10
  _Y212 = "Y212", Subsampling.YUV422, 12
  _444P = "444P", Subsampling.YUV444,  8
  _AYUV = "AYUV", Subsampling.YUV444,  8
  _VUYA = "VUYA", Subsampling.YUV444,  8
  _Y410 = "Y410", Subsampling.YUV444, 10
  _Y412 = "Y412", Subsampling.YUV444, 12
  _BGRA = "BGRA", Subsampling.NONE,    8
  _BGRX = "BGRX", Subsampling.NONE,    8
  _ARGB = "ARGB", Subsampling.NONE,    8

  def __str__(self):
    return self.value

  @property
  def subsampling(self):
    return self.__subsampling

  @property
  def bitdepth(self):
    return self.__bitdepth

  def is_compatible(self, other):
    pf = PixelFormat(other)
    return (
      self.subsampling == pf.subsampling
      and self.bitdepth == pf.bitdepth
    )

subsampling = {
  "Y800" : ("YUV400",  8),
  "I420" : ("YUV420",  8),
  "NV12" : ("YUV420",  8),
  "YV12" : ("YUV420",  8),
  "P010" : ("YUV420", 10),
  "P012" : ("YUV420", 12),
  "I010" : ("YUV420", 10),
  "422H" : ("YUV422",  8),
  "422V" : ("YUV422",  8),
  "YUY2" : ("YUV422",  8),
  "Y210" : ("YUV422", 10),
  "Y212" : ("YUV422", 12),
  "444P" : ("YUV444",  8),
  "AYUV" : ("YUV444",  8),
  "VUYA" : ("YUV444",  8),
  "Y410" : ("YUV444", 10),
  "Y412" : ("YUV444", 12),
}

def match_best_format(fmt, choices):
  if fmt in choices:
    return fmt
  matches = set(filter(lambda pf: pf.is_compatible(fmt), PixelFormat))
  matches &= set(choices)
  if len(matches) == 0:
    return None
  return list(matches)[0]

def get_bit_depth(fmt):
  return PixelFormat(fmt).bitdepth

class FormatMapper:
  def get_supported_format_map(self):
    raise NotImplementedError

  def get_supported_formats(self):
    return set(self.get_supported_format_map().keys())

  def map_format(self, format):
    return self.get_supported_format_map().get(format, None)

  def map_best_hw_format(self, format, hwformats):
    return self.map_format(
      match_best_format(
        format, set(hwformats) & set(self.get_supported_formats())))
