###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import json
import os
import slash
from .common import get_media, makepath, pathexists, abspath

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
    assert filename, "invalid filename"

    self.filename = abspath(filename)
    self.references = dict()
    self.rebase = rebase

    # load existing baseline references
    if pathexists(self.filename):
      if os.path.isdir(self.filename): # expanded reference files
        for root, dirs, files in os.walk(self.filename):
          for name in files:
            # ignore trendline model plots
            if name.endswith(".svg"): continue
            with open(os.path.join(root, name), "r") as fd:
              self.references.update(json.load(fd))
      else: # flat reference file for backwards compatibility
        with open(self.filename, "r") as fd:
          self.references = json.load(fd)

  def lookup(self, key, *context):
    reference = self.references.get(key, None)
    for c in get_media()._expand_context(context):
      if reference is None: break
      reference = reference.get(c, None)
    return reference

  def __get_reference(self, context = []):
    addr = get_media()._get_ref_addr(context)
    reference = self.references.setdefault(addr, dict())
    for c in get_media()._expand_context(context):
      reference = reference.setdefault(c, dict())
    return reference

  def update_reference(self, context = [], **kwargs):
    reference = self.__get_reference(context)
    reference.update(**kwargs)
    econtext = list(get_media()._expand_context(context))
    for key, val in kwargs.items():
      strkey = '.'.join(econtext + [key])
      get_media()._set_test_details(**{strkey:val})

  def check_result(self, compare, reference = None, context = [], **kwargs):
    if reference is None:
      reference = self.__get_reference(context)
      if self.rebase:
        reference.update(**kwargs)

    econtext = list(get_media()._expand_context(context))

    for key, val in kwargs.items():
      refval = reference.get(key, None)
      strkey = '.'.join(econtext + [key])
      get_media()._set_test_details(**{"{}:expect".format(strkey):refval})
      get_media()._set_test_details(**{"{}:actual".format(strkey):val})
      try:
        compare(key, refval, val)
        compareSuccess = True
      except:
        compareSuccess = False
        raise
      finally:
        get_media()._set_test_details(**{"{}:success".format(strkey):compareSuccess})

  def check_psnr(self, psnr, context = []):
    def compare(k, ref, actual):
      assert ref is not None, "Invalid reference value"
      assert all(map(lambda r,a: a > (r * 0.98), ref[3:], actual[3:]))
    self.check_result(compare = compare, context = context, psnr = psnr)

  def check_md5(self, md5, expect = None, context = []):
    def compare(k, ref, actual):
      assert ref == actual
    self.check_result(
      compare = compare,
      reference = None if expect is None else {"md5" : expect},
      context = context,
      md5 = md5)

  def finalize(self):
    if self.rebase:
      # expanded reference files by default
      if not pathexists(self.filename) or os.path.isdir(self.filename):
        # aggregate refs by testkey and testname
        refsbyfile = dict()
        for item in self.references.items():
          case, ref = item
          testkey, testcase = case.split(':')
          testname, params = testcase.split('(')
          reffile = os.path.join(self.filename, testkey, testname)
          refsbyfile.setdefault(reffile, dict())[case] = ref

        # dump aggregated refs into their own files
        for item in refsbyfile.items():
          reffile, refs = item
          makepath(os.path.dirname(reffile))
          with open(reffile, "w+") as fd:
            json.dump(
              refs, fd, cls = JSONFloatPrecisionEncoder, indent = 2,
              sort_keys = True
            )
      else: # flat reference file for backwards compatibility
        with open(self.filename, "w+") as fd:
          json.dump(
            self.references, fd, cls = JSONFloatPrecisionEncoder, indent = 2,
            sort_keys = True
          )
