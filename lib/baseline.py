###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import json
import os
import slash
from .common import get_media

class JSONFloatPrecisionEncoder(json.JSONEncoder):
  def iterencode(self, o):
    return json.encoder._make_iterencode(
      {}, self.default, json.encoder.encode_basestring_ascii,
      self.indent, "{:.4f}".format, self.key_separator, self.item_separator,
      self.sort_keys, self.skipkeys, True,
    )(o, 0)

################################################
# FIXME: Make Baseline work in parallel mode ###
################################################

class Baseline:
  def __init__(self, filename, rebase = False):
    self.filename = filename
    self.references = dict()
    self.rebase = rebase

    if self.filename and os.path.exists(self.filename):
      with open(self.filename, "r") as fd:
        self.references = json.load(fd)

  def __get_reference(self, context = []):
    addr = get_media()._get_ref_addr(context)
    reference = self.references.setdefault(addr, dict())
    for c in get_media()._expand_context(context):
      reference = reference.setdefault(c, dict())
    return reference

  def check_result(self, compare, context = [], **kwargs):
    reference = self.__get_reference(context)

    if self.rebase:
      reference.update(**kwargs)

    econtext = list(get_media()._expand_context(context))

    for key, val in kwargs.items():
      refval = reference.get(key, None)
      strkey = '.'.join(econtext + [key])
      get_media()._set_test_details(**{"{}:expect".format(strkey):refval})
      get_media()._set_test_details(**{"{}:actual".format(strkey):val})
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
      with open(self.filename, "w+") as fd:
        json.dump(
          self.references, fd, cls = JSONFloatPrecisionEncoder, indent = 2,
          sort_keys = True
        )
