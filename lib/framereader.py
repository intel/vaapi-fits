###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import numpy

def read_frame_422H(fd, width, height):
  width2  = (width + 1) / 2
  size    = width * height
  size2   = width2 * height

  y = numpy.fromfile(fd, dtype=numpy.uint8, count=size).reshape((height,width))
  u = numpy.fromfile(fd, dtype=numpy.uint8, count=size2).reshape((height,width2))
  v = numpy.fromfile(fd, dtype=numpy.uint8, count=size2).reshape((height,width2))

  return y, u, v

def read_frame_422V(fd, width, height):
  height2 = (height + 1) / 2
  size    = width * height
  size2   = width * height2

  y = numpy.fromfile(fd, dtype=numpy.uint8, count=size).reshape((height,width))
  u = numpy.fromfile(fd, dtype=numpy.uint8, count=size2).reshape((height2,width))
  v = numpy.fromfile(fd, dtype=numpy.uint8, count=size2).reshape((height2,width))

  return y, u, v

def read_frame_444P(fd, width, height):
  size = width * height

  y = numpy.fromfile(fd, dtype=numpy.uint8, count=size).reshape((height,width))
  u = numpy.fromfile(fd, dtype=numpy.uint8, count=size).reshape((height,width))
  v = numpy.fromfile(fd, dtype=numpy.uint8, count=size).reshape((height,width))

  return y, u, v

def read_frame_I420(fd, width, height):
  width2  = (width + 1) / 2
  height2 = (height + 1) / 2
  size    = width * height
  size2   = width2 * height2

  y = numpy.fromfile(fd, dtype=numpy.uint8, count=size).reshape((height, width))
  u = numpy.fromfile(fd, dtype=numpy.uint8, count=size2).reshape((height2, width2))
  v = numpy.fromfile(fd, dtype=numpy.uint8, count=size2).reshape((height2, width2))

  return y, u, v

def read_frame_Y800(fd, width, height):
  size = width * height

  y = numpy.fromfile(fd, dtype=numpy.uint8, count=size).reshape((height, width))

  return y, None, None

def read_frame_YV12(fd, width, height):
  width2  = (width + 1) / 2
  height2 = (height + 1) / 2
  size    = width * height
  size2   = width2 * height2

  y = numpy.fromfile(fd, dtype=numpy.uint8, count=size).reshape((height, width))
  v = numpy.fromfile(fd, dtype=numpy.uint8, count=size2).reshape((height2, width2))
  u = numpy.fromfile(fd, dtype=numpy.uint8, count=size2).reshape((height2, width2))

  return y, u, v

def read_frame_NV12(fd, width, height):
  width2  = (width + 1) / 2
  height2 = (height + 1) / 2
  size    = width * height
  size2   = width2 * height2 * 2

  y = numpy.fromfile(fd, dtype=numpy.uint8, count=size).reshape((height, width))
  uv = numpy.fromfile(fd, dtype=numpy.uint8, count=size2)

  return y, uv[0::2].reshape((height2, width2)), uv[1::2].reshape((height2, width2))

def read_frame_P010(fd, width, height):
  width2  = (width + 1) / 2
  height2 = (height + 1) / 2
  size    = width * height
  size2   = width2 * height2 * 2

  y = numpy.fromfile(fd, dtype=numpy.uint16, count=size).reshape((height, width))
  uv = numpy.fromfile(fd, dtype=numpy.uint16, count=size2)

  return y, uv[0::2].reshape((height2, width2)), uv[1::2].reshape((height2, width2))

def read_frame_AYUV(fd, width, height):
  size = width * height * 4

  ayuv = numpy.fromfile(fd, dtype=numpy.uint8, count=size)
  a = ayuv[0::4].reshape((height, width))
  y = ayuv[1::4].reshape((height, width))
  u = ayuv[2::4].reshape((height, width))
  v = ayuv[3::4].reshape((height, width))

  return y, u, v

def read_frame_YUY2(fd, width, height):
  size = width * height * 2

  yuv = numpy.fromfile(fd, dtype=numpy.uint8, count=size)

  # frames with odd width and height produce an odd number of bytes
  # in uv components and therefore cannot be effectively reshaped
  return yuv[0::2].reshape((height, width)), yuv[1::4], yuv[3::4]

def read_frame_ARGB(fd, width, height):
  size = width * height * 4

  argb = numpy.fromfile(fd, dtype=numpy.uint8, count=size)
  a = argb[0::4].reshape((height, width))
  r = argb[1::4].reshape((height, width))
  g = argb[2::4].reshape((height, width))
  b = argb[3::4].reshape((height, width))

  return r, g, b

def read_frame_BGRA(fd, width, height):
  size = width * height * 4

  argb = numpy.fromfile(fd, dtype=numpy.uint8, count=size)
  a = argb[3::4].reshape((height, width))
  r = argb[2::4].reshape((height, width))
  g = argb[1::4].reshape((height, width))
  b = argb[0::4].reshape((height, width))

  return r, g, b

def read_frame_P210(fd, width, height):
  width2  = (width + 1) / 2
  size    = width * height
  size2   = width2 * height

  y = numpy.fromfile(fd, dtype=numpy.uint16, count=size).reshape((height,width))
  u = numpy.fromfile(fd, dtype=numpy.uint16, count=size2).reshape((height,width2))
  v = numpy.fromfile(fd, dtype=numpy.uint16, count=size2).reshape((height,width2))

  return y, u, v

def read_frame_P410(fd, width, height):
  size = width * height

  y = numpy.fromfile(fd, dtype=numpy.uint16, count=size).reshape((height,width))
  u = numpy.fromfile(fd, dtype=numpy.uint16, count=size).reshape((height,width))
  v = numpy.fromfile(fd, dtype=numpy.uint16, count=size).reshape((height,width))

  return y, u, v

FrameReaders = {
  "I420" : read_frame_I420,
  "422H" : read_frame_422H,
  "422V" : read_frame_422V,
  "444P" : read_frame_444P,
  "NV12" : read_frame_NV12,
  "YV12" : read_frame_YV12,
  "P010" : read_frame_P010,
  "Y800" : read_frame_Y800,
  "YUY2" : read_frame_YUY2,
  "AYUV" : read_frame_AYUV,
  "ARGB" : read_frame_ARGB,
  "P210" : read_frame_P210,
  "P410" : read_frame_P410,
  "BGRA" : read_frame_BGRA,
}
