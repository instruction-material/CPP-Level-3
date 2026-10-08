"""Bound native curriculum checks and retain process cleanup evidence."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
TASK = os.environ.get('CLASSES_AUDIT_PARENT_TASK_ID', 'cppi5-native-source')
FLAGS = ['-Wall', '-Wextra', '-Wpedantic', '-Wconversion', '-Wsign-conversion',
         '-Werror', '-O0', '-g']


def cancel(signum, frame):
    raise SystemExit(128 + signum)


for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
    signal.signal(sig, cancel)


def flags(standard, sanitized):
    result = [f'-std=c++{standard}', *FLAGS]
    if sanitized:
        result += ['-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                   '-fno-omit-frame-pointer']
        if sys.platform.startswith('linux'):
            result += ['-fno-pie', '-no-pie']
    return result


def execute(command, cwd, expected=0, timeout=60):
    child = subprocess.Popen(command, cwd=cwd, start_new_session=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    fields = {'parentTaskId': TASK, 'parentPid': os.getpid(), 'pid': child.pid,
              'cwd': str(cwd), 'command': command, 'timeoutSeconds': timeout}

    def record(event, **extra):
        print(json.dumps({'event': event, **fields, **extra,
                          'time': datetime.now(timezone.utc).isoformat()}), flush=True)

    record('start')
    try:
        output, error = child.communicate(timeout=timeout)
    except BaseException:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
        record('child-process-group-cleanup', exitCode=child.returncode)
        raise
    record('end', exitCode=child.returncode)
    assert child.returncode == expected, (command, child.returncode, output, error)
    assert b'AddressSanitizer' not in error and b'runtime error:' not in error, error
    return output, error
