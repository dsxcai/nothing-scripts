#!/usr/bin/env python3
import subprocess
import sys
import time

if len(sys.argv) < 2:
    print('inavlid parameter(s)', file=sys.stderr)
    exit(-1)

ADB = sys.argv[1]

def list_devices():
    l = None
    if ADB != 'fastboot':
        l = subprocess.check_output(['adb', 'devices'], stderr=subprocess.PIPE, universal_newlines=True, timeout=3).splitlines();
        l = l[1:-1];
    else:
        l = subprocess.check_output([ADB, 'devices'], stderr=subprocess.PIPE, universal_newlines=True, timeout=3).splitlines();

    return [x.split()[0] for x in l]

def choose_devices(l):
    for i in range(len(l)):
        print('{}. {}'.format(i + 1, l[i]))
    print('a. All devices')
    c = input('? ')

    return (l if c == 'a' else [l[int(c) - 1]])

def execute(cmds=[], devices=[]):
    if len(devices) == 0:
        l = list_devices()
        if len(l) == 0:
            print('No device found.', file=sys.stderr)
            return (None, 0)
        else:
            devices = choose_devices(l)

    print(devices)
    proc = []
    for i in devices:
        _cmds = [ADB, '-s', i]
        _cmds.extend(cmds)
        print('run {} on {}'.format(_cmds, i))
        p = subprocess.Popen(_cmds, universal_newlines=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        proc.append((i, p))

    while len(proc) != 0:
        for i in proc:
            (d, p) = i
            if p.poll() is not None:
                print('### {} has terminated, return code: {}.'.format(d, p.returncode))
                print('### Output message:\n{}'.format(p.stdout.read()))
                print('### Output error message:\n{}'.format(p.stderr.read()))
                proc.remove((d, p))
            time.sleep(0.2)

execute(sys.argv[2:])
