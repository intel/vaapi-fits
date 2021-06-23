###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import psutil
import slash
import threading
import time

from ...lib.common import get_media, startproc, killproc

class MFXRuntimeTest(slash.Test):
  def expected(self, dispatcher):
    if "msdk" == dispatcher:
      return "msdk" if get_media()._get_gpu_gen() < 12.2 else "vpl"
    if "vpl" == dispatcher:
      return "msdk" if get_media()._get_gpu_gen() < 12 else "vpl"
    return None

  def check(self, command):
    proc = startproc(command)

    def readproc():
      for line in iter(proc.stdout.readline, ''):
        slash.logger.debug(line.rstrip('\n'))

    reader = threading.Thread(target = readproc)
    reader.daemon = True
    reader.start()

    time.sleep(5) # give proc some time to roll

    dispatcher = None
    runtimes = list()

    for m in psutil.Process(proc.pid).memory_maps():
      path = os.path.split(m.path)
      if path[-1].startswith("libmfxhw64.so"):
        runtimes.append("msdk")
      elif path[-1].startswith("libmfx-gen.so"):
        runtimes.append("vpl")
      elif path[-1].startswith("libmfx.so"):
        dispatcher = "msdk"
      elif path[-1].startswith("libvpl.so"):
        dispatcher = "vpl"

    expected_runtime = self.expected(dispatcher)
    get_media()._set_test_details(
      dispatcher        = dispatcher,
      runtimes          = runtimes,
      expected_runtime  = expected_runtime,
    )

    try:
      assert expected_runtime in runtimes
    finally:
      killproc(proc)
      proc.stdin.close()
      proc.stdout.close()
      reader.join(30)
