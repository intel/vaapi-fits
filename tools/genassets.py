#!/bin/env python2

###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import subprocess
import os
import sys


resolutions = [(176, 144), (320, 240), (1280, 720), (1920,1080),]

res_std = {
  (176, 144)  : "QCIF",
  (320, 240)  : "QVGA",
  (1280, 720) : "720p",
  (1920,1080) : "1080p",
}

formats = ["NV12",]

spec = dict(
  avc = dict(
    encoder = "vaapih264enc ! h264parse",
    decoder = "h264parse ! vaapih264dec",
    extension = "h264",
  ),
  hevc = dict(
    encoder = "vaapih265enc ! h265parse",
    decoder = "h265parse ! vaapih265dec",
    extension = "h265",
  ),
  jpeg = dict(
    encoder = "vaapijpegenc ! jpegparse",
    decoder = "jpegparse ! vaapijpegdec",
    extension = "mjpg",
  ),
  mpeg2 = dict(
    encoder = "vaapimpeg2enc ! mpegvideoparse",
    decoder = "mpegvideoparse ! vaapimpeg2dec",
    extension = "mpeg2",
  ),
  vp8 = dict(
    encoder = "vaapivp8enc ! matroskamux",
    decoder = "matroskademux ! vaapivp8dec",
    extension = "webm",
  ),
  vp9 = dict(
    encoder = "vaapivp9enc ! matroskamux",
    decoder = "matroskademux ! vaapivp9dec",
    extension = "webm",
  ),
)

for codec, params in spec.items():
  p = params.copy()
  p.update(path = "./assets/{}".format(codec))
  p.update(ypath = "./assets/yuv")
  p.update(codec = codec)

  if not os.path.exists(p["path"]):
    os.makedirs(p["path"])
  if not os.path.exists(p["ypath"]):
    os.makedirs(p["ypath"])

  for width, height in resolutions:
    p.update(width = width, height = height, resname = res_std[(width, height)])
    p.update(encoded = "{resname}.{extension}".format(**p))
    subprocess.check_call(
      "gst-launch-1.0 videotestsrc num-buffers=50 pattern=smpte"
        " ! video/x-raw,width={width},height={height}"
        " ! {encoder}"
        " ! filesink location={path}/{encoded}"
        "".format(**p),
      shell = True)
    for format in formats:
      if codec not in ["jpeg", "mpeg2"]:
        continue
      p.update(format = format)
      p.update(decoded = "{encoded}_ref.{format}.yuv".format(**p))
      subprocess.check_call(
        "gst-launch-1.0 filesrc location={path}/{encoded}"
          " ! {decoder}"
          " ! videoconvert ! video/x-raw,format={format},width={width},height={height}"
          " ! checksumsink2 file-checksum=false"
          " frame-checksum=false plane-checksum=false dump-output=true"
          " dump-location={ypath}/{decoded}"
          "".format(**p),
        shell = True)

for width, height in resolutions:
  for format in formats:
    subprocess.check_call(
      "gst-launch-1.0 videotestsrc num-buffers=300 pattern=smpte"
        " ! video/x-raw,width={width},height={height},format={format}"
        " ! checksumsink2 file-checksum=false frame-checksum=false"
        " plane-checksum=false dump-output=true"
        " dump-location=./assets/yuv/{resname}_{format}.yuv".format(
          width = width, height = height, format = format,
          resname = res_std[(width, height)]),
      shell = True)

subprocess.check_call("sync && tar cjvf assets.tbz2 assets", shell = True)
