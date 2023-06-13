###
### Copyright (C) 2018-2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ...lib.common import memoize

@memoize
def mapsharp(level):
  ###
  # MSDK uses the floor function to map the VPP scale range into the vaapi
  # driver VPP scale range.  The floor function is not invertible and therefore
  # we can't just reverse MSDK's mapping function with a simple mathematical
  # equation.  Additionally, MSDK does not take the default value (passthrough)
  # into account.  And, thus, we map 50 -> 0 directly to achieve normalization
  # at the expected passthrough/default level.
  #
  # This lookup table specifies the MSDK value to use from our normalized range
  # to produce the same result as if we were to map our normalized range
  # directly to the iHD driver range (i.e. [0, 50, 100] -> [0, 44, 64]).
  ###
  return {
                                        5: 6,  6: 8,  7: 9,  8:11,  9:11,
    10:12, 11:14, 12:15, 13:17, 14:18, 15:20, 16:22, 17:22, 18:23, 19:25,
    20:26, 21:28, 22:29, 23:31, 24:33, 25:34, 26:34, 27:36, 28:37, 29:39,
    30:40, 31:42, 32:43, 33:45, 34:45, 35:47, 36:48, 37:50, 38:51, 39:53,
    40:54, 41:56, 42:56, 43:58, 44:59, 45:61, 46:62, 47:64, 48:65, 49:67,
    50: 0, 51:68, 52:68, 53:70, 54:70, 55:72, 56:72, 57:72, 58:73, 59:73,
    60:75, 61:75, 62:75, 63:76, 64:76, 65:78, 66:78, 67:78, 68:79, 69:79,
    70:81, 71:81, 72:81, 73:83, 74:83, 75:84, 76:84, 77:84, 78:86, 79:86,
    80:87, 81:87, 82:87, 83:89, 84:89, 85:90, 86:90, 87:90, 88:92, 89:92,
    90:93, 91:93, 92:93, 93:95, 94:95, 95:97, 96:97, 97:97, 98:98, 99:98,
    100:98,
  }.get(level, level)
