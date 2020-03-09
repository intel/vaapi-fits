###
### Copyright (C) 2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

subsampling = {
  "Y800" : ("YUV400",  8),
  "I420" : ("YUV420",  8),
  "NV12" : ("YUV420",  8),
  "YV12" : ("YUV420",  8),
  "P010" : ("YUV420", 10),
  "422H" : ("YUV422",  8),
  "422V" : ("YUV422",  8),
  "YUY2" : ("YUV422",  8),
  "Y210" : ("YUV422", 10),
  "444P" : ("YUV444",  8),
  "AYUV" : ("YUV444",  8),
  "VUYA" : ("YUV444",  8),
  "Y410" : ("YUV444", 10),
}

def match_best_format(fmt, choices):
  if fmt in choices:
    return fmt
  matches = set([k for k,v in subsampling.items() if v == subsampling[fmt]])
  matches &= set(choices)
  if len(matches) == 0:
    return None
  return list(matches)[0]
