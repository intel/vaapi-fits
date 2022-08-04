###
### Copyright (C) 2018-2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import itertools
import os

from ..common import get_media, memoize
from ..framereader import FrameReaders

class RawFileFrameReader:
  def __init__(self, filename, width, height, nframes, fourcc):
    self.filename = filename
    self.width    = width
    self.height   = height
    self.nframes  = nframes
    self.fourcc   = fourcc
    self.reader   = FrameReaders[self.fourcc]

  # to support "with" syntax
  def __enter__(self):
    self.nreads = 0
    self.fd = open(self.filename, "rb")
    return self

  # to support "with" syntax
  def __exit__(self, type, value, tb):
    self.fd.close()

  def next_frame(self):
    try:
      return self.reader(self.fd, self.width, self.height)
    except Exception as e:
      e.args += tuple(["frame {}/{}".format(self.nreads, self.nframes)])
      raise
    finally:
      self.nreads += 1

class RawMetricAggregator:
  def __init__(self, biggest_deviator = min):
    self.results = list()
    self.biggest_deviator = biggest_deviator;

    # 50% of physical memory (i.e. 25% in main process and 25% in async pool)
    self.async_thresh = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 4
    self.async_results = list()
    self.async_bytes = 0

  def __collect_async(self):
    self.results.extend([r.get() for r in self.async_results])
    self.async_bytes = 0
    self.async_results = list()

  def __append(self, func, iterable):
    if get_media().metrics_pool is not None:
      self.async_results.append(
        get_media().metrics_pool.map_async(func, iterable))

      # Update bytes of yuv data that is being held by async_results
      self.async_bytes += sum([i.nbytes for i in itertools.chain(*iterable) if i is not None])

      # If we are holding onto too much yuv data, then we need to collect and
      # purge the current async_results to release the data
      if self.async_bytes >= self.async_thresh:
        self.__collect_async()
    else:
      self.results.append([func(i) for i in iterable])

  def __get(self):
    self.__collect_async()
    result = list(itertools.chain(*self.results))
    return [
      float(round(v, 4)) for v in (
        self.biggest_deviator(result[0::3]),
        self.biggest_deviator(result[1::3]),
        self.biggest_deviator(result[2::3]),
        sum(result[0::3]) / len(self.results),
        sum(result[1::3]) / len(self.results),
        sum(result[2::3]) / len(self.results),
      )
    ]

  def calculate(self, file1, file2, nframes, compare):
    with file1, file2: # this opens the files for reading
      for i in range(nframes):
        y1, u1, v1 = file1.next_frame()
        y2, u2, v2 = file2.next_frame()
        self.__append(compare, ((y1, y2), (u1, u2), (v1, v2)))
    return self.__get()

class MetricWithDataRange:
  def __init__(self, func, bitdepth):
    self.func = func
    self.data_range = pow(2, bitdepth) - 1

  def __call__(self, planes):
    return self.func(planes, self.data_range)

@memoize
def get_framesize(w, h, fourcc):
  w2  = (w + (w & 1)) >> 1;
  h2  = (h + (h & 1)) >> 1;
  szs = {
    "I420" : lambda: (w * h) + (w2 * h2 * 2),
    "422H" : lambda: (w * h) + (w2 * h * 2),
    "422V" : lambda: (w * h) + (w * h2 * 2),
    "444P" : lambda: w * h * 3,
    "NV12" : lambda: szs["I420"](),
    "YV12" : lambda: szs["I420"](),
    "P010" : lambda: szs["I420"]() * 2,
    "P012" : lambda: szs["I420"]() * 2,
    "I010" : lambda: szs["P010"](),
    "Y800" : lambda: w * h,
    "YUY2" : lambda: w * h * 2,
    "AYUV" : lambda: w * h * 4,
    "VUYA" : lambda: w * h * 4,
    "ARGB" : lambda: w * h * 4,
    "Y210" : lambda: w * h * 4,
    "Y212" : lambda: w * h * 4,
    "Y410" : lambda: w * h * 4,
    "Y412" : lambda: w * h * 8,
    "BGRA" : lambda: w * h * 4,
    "BGRX" : lambda: w * h * 4,
  }
  return szs[fourcc]()
