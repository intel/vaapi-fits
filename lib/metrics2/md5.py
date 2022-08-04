###
### Copyright (C) 2018-2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import hashlib
import os

from ..common import get_media, timefn
from . import factory

@timefn("md5:calculate")
def calculate(filename, chunksize = 4096, numbytes = -1):
  if numbytes < 0: # calculate checksum on entire file
    numbytes = os.stat(filename).st_size

  numbytesread = 0
  m = hashlib.md5()
  with open(filename, "rb") as f:
    # read numchunks of size chunksize
    numchunks = int(numbytes / chunksize)
    if numchunks > 0:
      for n, chunk in enumerate(iter(lambda: f.read(chunksize), b""), 1):
        numbytesread += len(chunk)
        m.update(chunk)
        if n == numchunks:
          break

    # read remainder of bytes < chunksize
    lastchunk = f.read(numbytes % chunksize)
    numbytesread += len(lastchunk)
    m.update(lastchunk)

  # fail if we did not read exactly numbytes
  assert numbytesread == numbytes, f"md5: expected {numbytes} bytes, got {numbytesread}"

  return m.hexdigest()

class MD5(factory.Metric):
  numbytes  = property(lambda self: self.props["metric"].get("numbytes", None))
  format    = property(lambda self: self.props.get("format2", super().format))

  @numbytes.setter
  def numbytes(self, value):
    self.props["metric"]["numbytes"] = value

  def update(self, **properties):
    super().update(**properties)
    if self.numbytes is not None and self.numbytes >= 0:
      self.numbytes = None

  def calculate(self):
    if self.numbytes is None:
      self.numbytes = self.framesize * self.frames
    return calculate(filename = self.filetest, numbytes = self.numbytes)

  def check(self):
    get_media().baseline.check_md5(
      md5 = self.actual, expect = self.expect, context = self.context)

factory.register(MD5)
