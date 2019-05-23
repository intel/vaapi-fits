from ...lib import *

import itertools
import os

__MYDIR__   = os.path.abspath(os.path.dirname(__file__))
__MYPARMS__ = list(
  itertools.product(
    [175, 176, 177],
    [143, 144, 145],
    ["I420", "NV12", "YV12", "P010", "AYUV", "YUY2", "ARGB", "422H", "444P",
    "P210", "P410"],
  )
)

def gen_multiframe_from(infile, count):
  outfile = get_media()._test_artifact(os.path.basename(infile))
  with open(infile, "rb") as fd:
    data = fd.read()
  with open(outfile, "wb") as fd:
    for i in xrange(count):
      fd.write(data)
  return outfile

@slash.parametrize(("width", "height", "fmt"), __MYPARMS__)
def test_get_framesize(width, height, fmt):
  asset = os.path.join(__MYDIR__, "assets", "{}x{}.{}").format(width, height, fmt)
  assert get_framesize(width, height, fmt) == os.stat(asset).st_size

@slash.parametrize(("width", "height", "fmt"), __MYPARMS__)
def test_check_filesize(width, height, fmt):
  asset = os.path.join(__MYDIR__, "assets", "{}x{}.{}").format(width, height, fmt)

  # single frame
  frames = 1
  check_filesize(asset, width, height, frames, fmt)

  # multi-frame
  frames = 31
  check_filesize(
    gen_multiframe_from(asset, frames), width, height, frames, fmt)

@slash.parametrize(("width", "height", "fmt"), __MYPARMS__)
def test_frame_reader(width, height, fmt):
  asset = os.path.join(__MYDIR__, "assets", "{}x{}.{}").format(width, height, fmt)
  frames = 27
  with open(gen_multiframe_from(asset, frames), "rb") as fd:
    size = get_framesize(width, height, fmt)
    for n in xrange(1, frames):
      y, u, v = FrameReaders[fmt](fd, width, height)
      assert fd.tell() == size * n
