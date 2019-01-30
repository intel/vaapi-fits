###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import hashlib
import itertools
import os
import skimage.measure

from common import get_media
from framereader import FrameReaders

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

class MetricsResult:
  def __init__(self, y, u, v):
    self.result = (y, u, v)

  def get(self):
    return self.result

def __compare_ssim(planes):
  a, b = planes
  if a is None or b is None: # handle Y800 case
    return 1.0
  return skimage.measure.compare_ssim(a, b, multichannel=True, win_size=3)

def calculate_ssim(filename1, filename2, width, height, nframes = 1, fourcc = "I420", fourcc2 = None):
  reader  = FrameReaders[fourcc]
  reader2 = FrameReaders[fourcc2 or fourcc]
  results = list()

  with open(filename1, "rb") as fd1, open(filename2, "rb") as fd2:
    for i in range(nframes):
      y1, u1, v1 = __try_read_frame(
        reader, fd1, width, height, debug = (i, nframes, 1))
      y2, u2, v2 = __try_read_frame(
        reader2, fd2, width, height, debug = (i, nframes, 2))

      if get_media().metrics_pool is not None:
        results.append(
          get_media().metrics_pool.map_async(
            __compare_ssim, ((y1, y2), (u1, u2), (v1, v2))
          )
        )
      else:
        results.append(
          MetricsResult(
            __compare_ssim((y1, y2)),
            __compare_ssim((u1, u2)),
            __compare_ssim((v1, v2))
          )
        )

  result = list(itertools.chain(*[r.get() for r in results]))

  return (
    min(result[0::3]),
    min(result[1::3]),
    min(result[2::3]),
    sum(result[0::3]) / nframes,
    sum(result[1::3]) / nframes,
    sum(result[2::3]) / nframes,
  )

def __compare_psnr(planes):
  a, b = planes
  if (a == b).all():
    # Avoid "Warning: divide by zero encountered in double_scalars" generated
    # by skimage.measure.compare_psnr when a and b are exactly the same.
    return 100
  return skimage.measure.compare_psnr(a, b)

def calculate_psnr(filename1, filename2, width, height, nframes = 1, fourcc = "I420"):
  reader  = FrameReaders[fourcc]
  results = list()

  with open(filename1, "rb") as fd1, open(filename2, "rb") as fd2:
    for i in range(nframes):
      y1, u1, v1 = __try_read_frame(
        reader, fd1, width, height, debug = (i, nframes, 1))
      y2, u2, v2 = __try_read_frame(
        reader, fd2, width, height, debug = (i, nframes, 2))

      if get_media().metrics_pool is not None:
        results.append(
          get_media().metrics_pool.map_async(
            __compare_psnr, ((y1, y2), (u1, u2), (v1, v2))
          )
        )
      else:
        results.append(
          MetricsResult(
            __compare_psnr((y1, y2)),
            __compare_psnr((u1, u2)),
            __compare_psnr((v1, v2))
          )
        )

  result = list(itertools.chain(*[r.get() for r in results]))

  return (
    min(result[0::3]),
    min(result[1::3]),
    min(result[2::3]),
    sum(result[0::3]) / nframes,
    sum(result[1::3]) / nframes,
    sum(result[2::3]) / nframes,
  )

def get_framesize(width, height, fourcc):
  return {
    "I420" : lambda w,h: w*h*3/2,
    "422H" : lambda w,h: w*h*2,
    "422V" : lambda w,h: w*h*2,
    "444P" : lambda w,h: w*h*3,
    "NV12" : lambda w,h: w*h*3/2,
    "YV12" : lambda w,h: w*h*3/2,
    "P010" : lambda w,h: w*h*6/2,
    "Y800" : lambda w,h: w*h,
    "YUY2" : lambda w,h: w*h*2,
    "AYUV" : lambda w,h: w*h*4,
  }[fourcc](width, height)

def check_filesize(filename, width, height, nframes, fourcc):
  expected = get_framesize(width, height, fourcc) * nframes
  actual = os.stat(filename).st_size
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
    numbytes = get_framesize(
      params["width"], params["height"],
      params.get("format2", params["format"])
    ) * params["frames"]
    res = md5(filename = params["decoded"], numbytes = numbytes)
    get_media().baseline.check_md5(
      md5 = res, context = params.get("refctx", []))

  else:
    assert False, "unknown metric"

