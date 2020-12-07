###
### Copyright (C) 2018-2020 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .parameters import format_value
import slash

def skip_test_if_missing_features(test):
  for feature in vars(test).get("features", list()):
    if not test.caps.get("features", dict()).get(feature, False):
      slash.skip_test(
        format_value(
          "{platform}.{driver}.feature({feature}) not supported",
          **vars(test), feature = feature))
