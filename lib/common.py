###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import slash
import subprocess
import threading
import time

class memoize:
  def __init__(self, function):
    self.function = function
    self.memoized = {}

  def __call__(self, *args):
    try:
      return self.memoized[args]
    except KeyError:
      r = self.function(*args)
      self.memoized[args] = r
      return r

  def __repr__(self):
    return str(self.function.__name__)

@memoize
def get_media():
  return slash.plugins.manager.get_plugin("media")

def killproc(proc):
  result = proc.poll()
  if result is not None:
    return result

  # try to 'gently' terminate proc
  proc.terminate()
  for i in xrange(5):
    result = proc.poll()
    if result is not None:
      return result
    time.sleep(1) # wait a little longer for proc to terminate

  # failed to terminate proc, so kill it
  proc.kill()
  for i in xrange(10):
    result = proc.poll()
    if result is not None:
      return result
    time.sleep(1) # give system more time to kill proc

  # failed to kill proc
  if result is None:
    slash.logger.warn('Failed to kill process with pid {}'.format(proc.pid))

  return result

def call(command, withSlashLogger = True):

  calls_allowed = get_media()._calls_allowed()
  assert calls_allowed, "call refused"

  if withSlashLogger:
    logger = slash.logger.info
  else:
    logger = lambda x: None

  def readproc(proc):
    for line in iter(proc.stdout.readline, ''):
      readproc.output += line
      logger(line.rstrip('\n'))
  readproc.output = ""

  def timeout(proc):
    timeout.triggered = proc.poll() is None
    killproc(proc)
  timeout.triggered = False

  error = False
  message = ""

  proc = subprocess.Popen(
    command,
    stdin = subprocess.PIPE,
    stdout = subprocess.PIPE,
    stderr = subprocess.STDOUT,
    shell = True)

  logger("CALL: {} (pid: {})".format(command, proc.pid))

  reader = threading.Thread(target = readproc, args = [proc])
  timer = threading.Timer(get_media().call_timeout, timeout, [proc])

  reader.daemon = True
  timer.daemon = True
  reader.start()
  timer.start()

  try: # in case of user interrupt
    proc.wait()
    timer.cancel()
  except:
    killproc(proc)
    raise
  finally:
    timer.cancel()
    timer.join(30)
    reader.join(30)

  if timeout.triggered:
    error = True
    get_media()._report_call_timeout()
    message = "CALL TIMEOUT: timeout after {} seconds (pid: {}).".format(
      get_media().call_timeout, proc.pid)
  elif proc.returncode != 0:
    error = True
    message = "CALL ERROR: failed with exitcode {} (pid: {})".format(proc.returncode, proc.pid)

  assert not error, message
  return readproc.output

def try_call(command):
  try:
    subprocess.check_output(command, stderr = subprocess.STDOUT, shell = True)
  except:
    return False
  return True

def mapRange(value, srcRange, destRange):
  (smin, smax), (dmin, dmax) = srcRange, destRange
  return dmin + ((value - smin) * (dmax - dmin) / (smax - smin))
