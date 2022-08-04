###
### Copyright (C) 2018-2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os

from ..common import get_media
from .util import get_framesize
from . import factory

class Filesize(factory.Metric):
  def calculate(self):
    return os.stat(self.filetest).st_size

  def check(self):
    expected = self.framesize * self.frames

    get_media()._set_test_details(**{"filesize:expect" : expected})
    get_media()._set_test_details(**{"filesize:actual" : self.actual})

    assert expected == self.actual

factory.register(Filesize)
