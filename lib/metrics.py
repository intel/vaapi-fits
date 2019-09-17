###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import hashlib
import itertools
import os
import skimage.measure

from common import get_media, memoize, timefn
from framereader import FrameReaders

@timefn("md5")
def md5(filename, chunksize = 4096, numbytes = -1):
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
  assert numbytesread == numbytes, "md5: expected {} bytes, got {}".format(numbytes, numbytesread)

  return m.hexdigest()

def __try_read_frame(reader, *args, **kwargs):
  try:
    return reader(*args)
  except Exception, e:
    e.args += tuple("{}: {}".format(k,v) for k,v in kwargs.items())
    raise

class YUVMetricAggregator:
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

  def append(self, func, iterable):
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

  def get(self):
    self.__collect_async()
    result = list(itertools.chain(*self.results))
    return map(
      lambda v: round(v, 4), (
        self.biggest_deviator(result[0::3]),
        self.biggest_deviator(result[1::3]),
        self.biggest_deviator(result[2::3]),
        sum(result[0::3]) / len(self.results),
        sum(result[1::3]) / len(self.results),
        sum(result[2::3]) / len(self.results),
      )
    )

def __compare_ssim(planes):
  a, b = planes
  if a is None or b is None: # handle Y800 case
    return 1.0
  return skimage.measure.compare_ssim(a, b, win_size = 3)

@timefn("ssim")
def calculate_ssim(filename1, filename2, width, height, nframes = 1, fourcc = "I420", fourcc2 = None):
  reader  = FrameReaders[fourcc]
  reader2 = FrameReaders[fourcc2 or fourcc]
  aggregator = YUVMetricAggregator()

  with open(filename1, "rb") as fd1, open(filename2, "rb") as fd2:
    for i in xrange(nframes):
      y1, u1, v1 = __try_read_frame(
        reader, fd1, width, height, debug = (i, nframes, 1))
      y2, u2, v2 = __try_read_frame(
        reader2, fd2, width, height, debug = (i, nframes, 2))

      aggregator.append(__compare_ssim, ((y1, y2), (u1, u2), (v1, v2)))

  return aggregator.get()

def __compare_psnr(planes):
  a, b = planes
  if (a == b).all():
    # Avoid "Warning: divide by zero encountered in double_scalars" generated
    # by skimage.measure.compare_psnr when a and b are exactly the same.
    return 100
  return skimage.measure.compare_psnr(a, b)

@timefn("psnr")
def calculate_psnr(filename1, filename2, width, height, nframes = 1, fourcc = "I420"):
  reader = FrameReaders[fourcc]
  aggregator = YUVMetricAggregator()

  with open(filename1, "rb") as fd1, open(filename2, "rb") as fd2:
    for i in xrange(nframes):
      y1, u1, v1 = __try_read_frame(
        reader, fd1, width, height, debug = (i, nframes, 1))
      y2, u2, v2 = __try_read_frame(
        reader, fd2, width, height, debug = (i, nframes, 2))

      aggregator.append(__compare_psnr, ((y1, y2), (u1, u2), (v1, v2)))

  return aggregator.get()

def __compare_mse(planes):
  a, b = planes
  return skimage.measure.compare_mse(a, b)

@timefn("mse")
def calculate_mse(filename1, filename2, width, height, nframes = 1, fourcc = "I420"):
  reader = FrameReaders[fourcc]
  aggregator = YUVMetricAggregator(max)

  with open(filename1, "rb") as fd1, open(filename2, "rb") as fd2:
    for i in xrange(nframes):
      y1, u1, v1 = __try_read_frame(
        reader, fd1, width, height, debug = (i, nframes, 1))
      y2, u2, v2 = __try_read_frame(
        reader, fd2, width, height, debug = (i, nframes, 2))

      aggregator.append(__compare_mse, ((y1, y2), (u1, u2), (v1, v2)))

  return aggregator.get()

def __compare_nrmse(planes):
  a, b = planes
  return skimage.measure.compare_nrmse(a, b, norm_type = "Euclidean")

@timefn("nrmse")
def calculate_nrmse(filename1, filename2, width, height, nframes = 1, fourcc = "I420"):
  reader = FrameReaders[fourcc]
  aggregator = YUVMetricAggregator(max)

  with open(filename1, "rb") as fd1, open(filename2, "rb") as fd2:
    for i in xrange(nframes):
      y1, u1, v1 = __try_read_frame(
        reader, fd1, width, height, debug = (i, nframes, 1))
      y2, u2, v2 = __try_read_frame(
        reader, fd2, width, height, debug = (i, nframes, 2))

      aggregator.append(__compare_nrmse, ((y1, y2), (u1, u2), (v1, v2)))

  return aggregator.get()

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
    "Y800" : lambda: w * h,
    "YUY2" : lambda: w * h * 2,
    "AYUV" : lambda: w * h * 4,
    "ARGB" : lambda: w * h * 4,
    "P210" : lambda: szs["422H"]() * 2,
    "P410" : lambda: w * h * 6,
    "BGRA" : lambda: w * h * 4,
  }
  return szs[fourcc]()

def check_filesize(filename, width, height, nframes, fourcc):
  expected = get_framesize(width, height, fourcc) * nframes
  actual = os.stat(filename).st_size

  get_media()._set_test_details(**{"filesize:expect":expected})
  get_media()._set_test_details(**{"filesize:actual":actual})

  assert expected == actual

def check_metric(**params):
  metric = params["metric"]
  type = metric["type"]

  if "ssim" == type:
    miny = metric.get("miny", 1.0)
    minu = metric.get("minu", 1.0)
    minv = metric.get("minv", 1.0)
    ssim = calculate_ssim(
      params["reference"], params["decoded"],
      params["width"], params["height"], params["frames"],
      params["format"], params.get("format2", None))
    get_media()._set_test_details(ssim = ssim)
    assert 1.0 >= ssim[0] >= miny
    assert 1.0 >= ssim[1] >= minu
    assert 1.0 >= ssim[2] >= minv

  elif "md5" == type:
    numbytes = metric.get("numbytes", get_framesize(
      params["width"], params["height"],
      params.get("format2", params["format"])
    ) * params["frames"])
    res = md5(filename = params["decoded"], numbytes = numbytes)
    get_media().baseline.check_md5(
      md5 = res, context = params.get("refctx", []))

  elif "psnr" == type:
    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        params["reference"], params["decoded"],
        params["width"], params["height"], params["frames"],
        params["format"]),
      context = params.get("refctx", []))

  elif "mse" == type:
    mse = calculate_mse(
      params["reference"], params["decoded"],
      params["width"], params["height"],
      params["frames"], params["format"])
    get_media()._set_test_details(mse = mse)
    avg_range = metric.get("avg_range", [(0, 256), (0, 256), (0, 256)])
    assert avg_range[0][0] <= mse[-3] <= avg_range[0][1]
    assert avg_range[1][0] <= mse[-2] <= avg_range[1][1]
    assert avg_range[2][0] <= mse[-1] <= avg_range[2][1]

  elif "nrmse" == type:
    nrmse = calculate_nrmse(
      params["reference"], params["decoded"],
      params["width"], params["height"],
      params["frames"], params["format"])
    get_media()._set_test_details(nrmse = nrmse)
    avg_range = metric.get("avg_range", [(0, 0.07), (0, 0.07), (0, 0.07)])
    assert avg_range[0][0] <= nrmse[-3] <= avg_range[0][1]
    assert avg_range[1][0] <= nrmse[-2] <= avg_range[1][1]
    assert avg_range[2][0] <= nrmse[-1] <= avg_range[2][1]

  else:
    assert False, "unknown metric"

