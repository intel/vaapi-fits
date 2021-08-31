###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import types

class PropertyHandler:
  def __init__(self, **properties):
    self.props = dict()
    self.update(**properties)

  def update(self, **properties):
    self.props.update(**properties)

  def ifprop(self, prop, val):
    v = self.props.get(prop, None)
    if type(val) in [types.FunctionType, types.MethodType]:
      result = val(v) if v is not None else ""
    else:
      result = val if v is not None else ""
    return result.format(**self.props)
