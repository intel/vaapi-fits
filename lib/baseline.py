###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import json
import os
import slash
from common import get_media

################################################
# FIXME: Make Baseline work in parallel mode ###
################################################

class Baseline:
  def __init__(self, filename, rebase = False):
    self.filename = filename
    self.references = dict()
    self.actuals = dict()
    self.rebase = rebase

    if self.filename and os.path.exists(self.filename):
      with open(self.filename, "rb") as fd:
        self.references = json.load(fd)

  def __get_reference(self, addr, context = []):
    reference = self.references.setdefault(addr, dict())
    for c in sorted(context):
      c = c.strip().lower()
      if "driver" == c:
        c = "drv.{}".format(get_media()._get_driver_name())
      reference = reference.setdefault(c, dict())
    return reference

  def check_result(self, compare, context = [], **kwargs):
    addr = slash.context.test.__slash__.address
    actual = self.actuals.setdefault(addr, dict())
    reference = self.__get_reference(addr, context)

    actual.update(**kwargs)
    if self.rebase:
      reference.update(**kwargs)

    for key, val in kwargs.iteritems():
      refval = reference.get(key, None)
      get_media()._set_test_details(**{key:val})
      get_media()._set_test_details(**{"ref_{}".format(key):refval})
      compare(key, refval, val)

  def check_psnr(self, psnr, context = []):
    def compare(k, ref, actual):
      assert ref is not None, "Invalid reference value"
      assert all(map(lambda r,a: a+0.2 > r, ref[3:], actual[3:]))
    self.check_result(compare, context, psnr = psnr)

  def check_md5(self, md5, context = []):
    def compare(k, ref, actual):
      assert ref == actual
    self.check_result(compare, context, md5 = md5)

  def finalize(self):
    if self.rebase:
      if not os.path.exists(os.path.dirname(self.filename)):
        os.makedirs(os.path.dirname(self.filename))
      with open(self.filename, "wb+") as fd:
        json.dump(self.references, fd, indent = 2, sort_keys = True)

