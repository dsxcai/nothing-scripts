#!/usr/bin/env python3

import xml.etree.ElementTree
import sys
import json

e = xml.etree.ElementTree.parse(sys.argv[1])

r = e.getroot()

l = {'0-': {}, '1-': {}, '2-': {}, '3-': {}, '4-': {}, '5-': {}, '6-': {},}
settings = {}

for i in r:
    name = i.get('name')
    val = i.get('value')
    tag = i.tag
    data = i.text if val is None else val
    print('{} {} {} {}'.format(name, val, tag, i.text))

    if name.startswith('res'):
        if name.endswith('0-'):
            l['0-'].update({'Name': 'CoreMark-Pro (Base)', 'Score': data})
        elif name.endswith('0-0'):
            l['0-'].update({'Linear Single Core': data})
        elif name.endswith('0-1'):
            l['0-'].update({'Loops Single Core': data})
        elif name.endswith('0-2'):
            l['0-'].update({'NNET Single Core': data})
        elif name.endswith('0-3'):
            l['0-'].update({'FFT Single Core': data})
        elif name.endswith('0-4'):
            l['0-'].update({'SHA256 Single Core': data})
        elif name.endswith('0-5'):
            l['0-'].update({'XML Single Core': data})
        elif name.endswith('0-6'):
            l['0-'].update({'ZIP Single Core': data})
        elif name.endswith('0-7'):
            l['0-'].update({'CJPEG Single Core': data})
        elif name.endswith('0-8'):
            l['0-'].update({'CORE Single Core': data})
        elif name.endswith('0-9'):
            l['0-'].update({'Linear Multi Core': data})
        elif name.endswith('0-10'):
            l['0-'].update({'Loops Multi Core': data})
        elif name.endswith('0-11'):
            l['0-'].update({'NNET Multi Core': data})
        elif name.endswith('0-12'):
            l['0-'].update({'FFT Multi Core': data})
        elif name.endswith('0-13'):
            l['0-'].update({'SHA256 Multi Core': data})
        elif name.endswith('0-14'):
            l['0-'].update({'XML Multi Core': data})
        elif name.endswith('0-15'):
            l['0-'].update({'ZIP Multi Core': data})
        elif name.endswith('0-16'):
            l['0-'].update({'CJPEG Multi Core': data})
        elif name.endswith('0-17'):
            l['0-'].update({'CORE Multi Core': data})
        elif name.endswith('1-'):
            l['1-'].update({'Name': 'CoreMark-Pro (Peak)', 'Score': data})
        elif name.endswith('2-'):
            l['2-'].update({'Name': 'Memory Bandwidth', 'Score': data})
        elif name.endswith('2-0'):
            l['2-'].update({'Copy Single Core': data})
        elif name.endswith('2-1'):
            l['2-'].update({'Scale Single Core': data})
        elif name.endswith('2-2'):
            l['2-'].update({'Add Single Core': data})
        elif name.endswith('2-3'):
            l['2-'].update({'Triad Single Core': data})
        elif name.endswith('2-4'):
            l['2-'].update({'Copy Multi Core': data})
        elif name.endswith('2-5'):
            l['2-'].update({'Scale Multi Core': data})
        elif name.endswith('2-6'):
            l['2-'].update({'Add Multi Core': data})
        elif name.endswith('2-7'):
            l['2-'].update({'Triad Multi Core': data})
        elif name.endswith('3-'):
            l['3-'].update({'Name': 'Memory Latency', 'Score': data})
        elif name.endswith('3-0'):
            l['3-'].update({'64M range': data})
        elif name.endswith('4-'):
            l['4-'].update({'Name': 'Storage', 'Score': data})
        elif name.endswith('4-0'):
            l['4-'].update({'512B WS': data})
        elif name.endswith('4-1'):
            l['4-'].update({'512B WR': data})
        elif name.endswith('4-2'):
            l['4-'].update({'512B RR': data})
        elif name.endswith('4-3'):
            l['4-'].update({'512B RS': data})
        elif name.endswith('4-4'):
            l['4-'].update({'4K WS': data})
        elif name.endswith('4-5'):
            l['4-'].update({'4K RR': data})
        elif name.endswith('4-6'):
            l['4-'].update({'4K WR': data})
        elif name.endswith('4-7'):
            l['4-'].update({'4K RS': data})
        elif name.endswith('4-8'):
            l['4-'].update({'16K WS': data})
        elif name.endswith('4-9'):
            l['4-'].update({'16K RR': data})
        elif name.endswith('4-10'):
            l['4-'].update({'16K WR': data})
        elif name.endswith('4-11'):
            l['4-'].update({'16K RS': data})
        elif name.endswith('4-12'):
            l['4-'].update({'256K RS': data})
        elif name.endswith('4-13'):
            l['4-'].update({'256K RR': data})
        elif name.endswith('5-'):
            l['5-'].update({'Name': 'Platform', 'Score': data})
        elif name.endswith('5-0'):
            l['5-'].update({'RC4': data})
        elif name.endswith('5-1'):
            l['5-'].update({'SHA256': data})
        elif name.endswith('5-2'):
            l['5-'].update({'Unzip': data})
        elif name.endswith('5-3'):
            l['5-'].update({'DB Build': data})
        elif name.endswith('5-4'):
            l['5-'].update({'DB Query': data})
        elif name.endswith('5-5'):
            l['5-'].update({'Effects': data})
        elif name.endswith('5-6'):
            l['5-'].update({'ZIP': data})
        elif name.endswith('5-7'):
            l['5-'].update({'AES': data})
        elif name.endswith('5-8'):
            l['5-'].update({'Sign': data})
        elif name.endswith('5-9'):
            l['5-'].update({'Output': data})
        elif name.endswith('6-'):
            l['6-'].update({'Name': '3D', 'Score': data})
        elif name.endswith('6-0'):
            l['6-'].update({'FPS': data})
        else:
            l.update({name: data})
    else:
        settings[name] = data

for i in l:
    if 'Name' in l[i]:
        l[l[i]['Name']] = l[i]
        l[l[i]['Name']].pop('Name')
        l.pop(i)

l['Settings'] = settings

print(json.dumps(l, indent=4, sort_keys=True))
