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

case_parameter_list = {}
def skip_test_by_parameter(class_name, skip_lst, **kwargs):
    if class_name not in case_parameter_list:
      case_parameter_list[class_name] = list()
    case_dict = case_parameter_list[class_name]
    parameter_str = ''
    for k,v in kwargs.items():
      if k in skip_lst:
        slash.logger.notice("NOTICE: '{}' parameter unused (not supported by plugin)".format(k))
      else:
        parameter_str += '{}={} '.format(k, v)

    if parameter_str not in case_dict:
      case_dict.append(parameter_str)
    else:
      slash.skip_test("{} already run, because '{}' unused".format(parameter_str, ','.join(skip_lst)))
