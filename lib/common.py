###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from datetime import datetime as dt
import functools
import os
import slash
import subprocess
import threading
import time

def sorted_by_resolution(cases):
  size = lambda kv: kv[1]["width"] * kv[1]["height"]
  return [kv[0] for kv in sorted(cases.items(), key = size)]

def timefn(label):
  def count(function):
    # Keep track of the number of times this function was called from the
    # current test context.  This allows us to use a unique label for the
    # test details.
    count = get_media()._test_state_value(function, 0)
    count.value += 1
    return count.value

  def inner(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      start = dt.now()
      try:
        ret = function(*args, **kwargs)
      except:
        raise
      finally:
        stotal = (dt.now() - start).total_seconds()
        kdetail = "time({}:{})".format(label, count(function))
        get_media()._set_test_details(**{kdetail : "{:.4f}s".format(stotal)})
      return ret
    return wrapper

  return inner

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
  for i in range(5):
    result = proc.poll()
    if result is not None:
      return result
    time.sleep(1) # wait a little longer for proc to terminate

  # failed to terminate proc, so kill it
  proc.kill()
  for i in range(10):
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
    import sys
    for line in iter(proc.stdout.readline, b''):
      # check python version
      if sys.version_info.major == 2:
        readproc.output += line
        logger(line.rstrip('\n'))
      else:
        readproc.output += line.decode("utf-8")
        logger(line.decode("utf-8").rstrip().rstrip('\n'))
  readproc.output = ""

  def timeout(proc):
    timeout.triggered = proc.poll() is None
    killproc(proc)
  timeout.triggered = False

  error = False
  message = ""

  # Without "exec", the shell will launch the "command" in a child process and
  # proc.pid will represent the shell (not the "command").  And therefore, the
  # "command" will not get killed with proc.terminate() or proc.kill().
  #
  # When we use "exec" to run the "command". This will cause the "command" to
  # inherit the shell process and proc.pid will represent the actual "command".
  proc = subprocess.Popen(
    "exec " + command,
    stdin = subprocess.PIPE,
    stdout = subprocess.PIPE,
    stderr = subprocess.STDOUT,
    shell = True)

  logger("CALL: {} (pid: {})".format(command, proc.pid))

  reader = threading.Thread(target = readproc, args = [proc])
  timer = threading.Timer(get_media()._get_call_timeout(), timeout, [proc])
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
    proc.stdin.close()
    proc.stdout.close()

  if timeout.triggered:
    error = True
    get_media()._report_call_timeout()
    message = "CALL TIMEOUT: timeout after {} seconds (pid: {}).".format(
      timer.interval, proc.pid)
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
