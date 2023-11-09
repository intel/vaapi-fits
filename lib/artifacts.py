###
### Copyright (C) 2023 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash
from enum import Enum

Scope     = Enum("Scope", dict(TEST = "test", SESSION = "session-global"), type = str)
Retention = Enum("Retention", ["NONE", "FAIL", "ALL"], start = 0, type = int)

class Artifacts():
  def __init__(self, retention):
    self._retention = Retention(retention)

  @property
  def retention(self):
    return self._retention

  def __result(self, scope):
    return {
      Scope.TEST    : slash.context.result,
      Scope.SESSION : slash.session.results.global_result
    }[scope]

  def __id(self, scope):
    return {
      Scope.TEST    : slash.context.test.id,
      Scope.SESSION : slash.session.id,
    }[scope]

  def purge(self, filename, scope = Scope.TEST):
    result = self.__result(scope)
    if Retention.ALL != self.retention:
      if Retention.FAIL == self.retention and not result.is_success():
        pass # Keep artifact on failure
      elif filename in result.data.get("artifacts", list()):
        if os.path.exists(filename):
          os.remove(filename)

  def reserve(self, ext, scope = Scope.TEST):
    result = self.__result(scope)
    artifacts = result.data.setdefault("artifacts", list())
    filename = f"{self.__id(scope)}_{len(artifacts)}.{ext}"
    absfile = os.path.join(result.get_log_dir(), filename)
    artifacts.append(absfile)
    slash.add_critical_cleanup(self.purge, scope = scope, args = (absfile, scope))
    return absfile

