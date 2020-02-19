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
    for i in range(count):
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
    for n in range(1, frames):
      y, u, v = FrameReaders[fmt](fd, width, height)
      assert fd.tell() == size * n

@slash.parametrize(("width", "height"), itertools.product([175, 176, 177], [143, 144, 145]))
def test_frame_reader_Y410(width, height):
  testfile = get_media()._test_artifact(
    "test_frame_reader_Y410_{}x{}.Y410".format(width, height))
  a = 3; oy = 512; ou = 256; ov = 128;
  dword = (a << 30) | (ov << 20) | (oy << 10) | ou
  b = dword.to_bytes(4, "little")
  with open(testfile, "wb") as fd:
    for i in range(width * height):
      fd.write(b)

  with open(testfile, "rb") as fd:
    y, u, v = read_frame_Y410(fd, width, height)

    yf = lambda val: val == oy
    uf = lambda val: val == ou
    vf = lambda val: val == ov

    assert y.size == u.size == v.size == width * height
    assert fd.tell() == get_framesize(width, height, "Y410")
    assert yf(y).all()
    assert uf(u).all()
    assert vf(v).all()
