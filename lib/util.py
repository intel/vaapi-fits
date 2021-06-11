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

def load_test_spec(component, *ctx):
  from .common import get_media
  import copy

  # get copy of general ctx entries
  spec = copy.deepcopy(get_media()._get_test_spec(*ctx))

  # remove cases that explicitly don't want to use this component
  for k, v in list(spec.items()):
    if component in set(v.get("not_components", set())):
      del spec[k]

  # component specific entries override general ctx entries
  spec.update(get_media()._get_test_spec(component, *ctx))

  return spec
