###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import hashlib
import itertools
import os

from .common import get_media, memoize, timefn
from .framereader import FrameReaders

try:
  # try skimage >= 0.16, first
  from skimage.metrics import structural_similarity as skimage_ssim
except:
  from skimage.measure import compare_ssim as skimage_ssim

try:
  # try skimage >= 0.16, first
  from skimage.metrics import peak_signal_noise_ratio as skimage_psnr
except:
  from skimage.measure import compare_psnr as skimage_psnr

try:
  # try skimage >= 0.16, first
  from skimage.metrics import mean_squared_error as skimage_mse
except:
  from skimage.measure import compare_mse as skimage_mse

try:
  # try skimage >= 0.16, first
  from skimage.metrics import normalized_root_mse as skimage_nrmse
except:
  from skimage.measure import compare_nrmse as skimage_nrmse

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

class RawFile:
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

def __compare_ssim(planes):
  a, b = planes
  if a is None or b is None: # handle Y800 case
    return 1.0
  return skimage_ssim(a, b, win_size = 3)

@timefn("ssim")
def calculate_ssim(filename1, filename2, width, height, nframes = 1, fourcc = "I420", fourcc2 = None):
  return RawMetricAggregator(min).calculate(
    RawFile(filename1, width, height, nframes, fourcc),
    RawFile(filename2, width, height, nframes, fourcc2 or fourcc),
    nframes, __compare_ssim)

def __compare_psnr(planes):
  a, b = planes
  if (a == b).all():
    # Avoid "Warning: divide by zero encountered in double_scalars" generated
    # by skimage.measure.compare_psnr when a and b are exactly the same.
    return 100
  return skimage_psnr(a, b)

@timefn("psnr")
def calculate_psnr(filename1, filename2, width, height, nframes = 1, fourcc = "I420"):
  return RawMetricAggregator(min).calculate(
    RawFile(filename1, width, height, nframes, fourcc),
    RawFile(filename2, width, height, nframes, fourcc),
    nframes, __compare_psnr)

def __compare_mse(planes):
  a, b = planes
  return skimage_mse(a, b)

@timefn("mse")
def calculate_mse(filename1, filename2, width, height, nframes = 1, fourcc = "I420"):
  return RawMetricAggregator(max).calculate(
    RawFile(filename1, width, height, nframes, fourcc),
    RawFile(filename2, width, height, nframes, fourcc),
    nframes, __compare_mse)

def __compare_nrmse(planes):
  a, b = planes
  return skimage_nrmse(a, b)

@timefn("nrmse")
def calculate_nrmse(filename1, filename2, width, height, nframes = 1, fourcc = "I420"):
  return RawMetricAggregator(max).calculate(
    RawFile(filename1, width, height, nframes, fourcc),
    RawFile(filename2, width, height, nframes, fourcc),
    nframes, __compare_nrmse)

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
      md5 = res,
      expect = metric.get("expect", None),
      context = params.get("refctx", []))

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

