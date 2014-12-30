#!/usr/bin/python3


import argparse
import sys
import struct

from pattern import *


def main(argv=None):
    argparser = argparse.ArgumentParser()
    needle_group = argparser.add_mutually_exclusive_group(required=True)
    needle_group.add_argument('needle', nargs='?')
    needle_group.add_argument('--needle-string')
    haystack_group = argparser.add_mutually_exclusive_group()
    haystack_group.add_argument('-f', '--haystack-file')
    haystack_group.add_argument('sets', nargs='*',
                                default=DEFAULT_PATTERN_SETS)
    argparser.add_argument('-l', '--length', type=int, default=None)
    argparser.add_argument('--fuzzy', action='store_true')
    argparser.add_argument('-m', '--metasploit', action='store_true')
    if argv is None:
        args = argparser.parse_args()
    else:
        args = argparser.parse_args(argv)

    if args.needle_string:
        needle = args.needle_string
    elif len(args.needle) == 4:
            needle = args.needle.encode('utf-8')
    else:
        try:
            needle_digits = (args.needle[2:] if args.needle[:2] == '0x'
                             else args.needle)
            needle = struct.pack('<I', int(needle_digits, 16))
        except ValueError:
            needle = args.needle.encode('utf-8')

    if args.haystack_file:
        with open(args.haystack_file, 'rb') as f:
            haystack = f.read()
    else:
        haystack = ''.join(pattern_create(args.length, args.sets,
                                          allow_repeats=True)).encode('utf-8')

    offset = haystack.find(needle)
    found_any = False
    while offset != -1:
        found_any = True
        if args.metasploit:
            print('[*] Exact match at offset {}'.format(offset))
        else:
            print(offset)
        offset = haystack.find(needle, offset + 1)
    if found_any:
        return 0

    if args.metasploit:
        print('[*] No exact matches, looking for likely candidates...',
              file=sys.stderr)
    else:
        print('No exact matches.', file=sys.stderr)
        if args.fuzzy:
            print('Looking for likely candidates...', file=sys.stderr)
        else:
            return 255

    if not args.metasploit:
        print('Looking for endian reversal...', file=sys.stderr)
        new_needle = struct.pack('>I', struct.unpack('<I', needle)[0])
        found_any = False
        offset = haystack.find(new_needle)
        while offset != -1:
            found_any = True
            print('Endian-reversed match at offset {}'.format(offset))
            offset = haystack.find(new_needle, offset + 1)
        if found_any:
            return 254

    found_any = False
    for i in range(len(needle)):
        for c in range(256):
            new_needle = needle[:i] + bytes([c]) + needle[i + 1:]
            offset = haystack.find(new_needle)
            while offset != -1:
                found_any = True
                if args.metasploit:
                    needle_int = struct.unpack('<I', needle)[0]
                    mle = needle_int - struct.unpack('<I', new_needle)[0]
                    mbe = needle_int - struct.unpack('>I', new_needle)[0]
                    print('[+] Possible match at offset {} '
                          '(adjusted [ little-endian: {} | big-endian: {} ] ) '
                          'byte offset {}'.format(offset, mle, mbe, i))
                else:
                    print('Single-byte-shifted match {} at offset {}'.format(
                            new_needle, offset))
                offset = haystack.find(new_needle, offset + 1)
    if found_any:
        return 254

    if not args.metasploit:
        print('Looking for double-byte shifts...')

    found_any = False
    for i in range(0, len(needle), 2):
        for c1 in range(256):
            for c2 in range(256):
                new_needle = needle[:i] + bytes([c1, c2]) + needle[i+2:]
                offset = haystack.find(new_needle)
                while offset != -1:
                    found_any = True
                    if args.metasploit:
                        needle_int = struct.unpack('<I', needle)[0]
                        mle = needle_int - struct.unpack('<I', new_needle)[0]
                        mbe = needle_int - struct.unpack('>I', new_needle)[0]
                        print('[+] Possible match at offset {} '
                              '(adjusted [ little-endian: {} '
                              '| big-endian: {} ] )'.format(offset, mle, mbe))
                    else:
                        print(
                            'Double-byte-shifted match {} at offset {}'.format(
                                new_needle, offset))
                    offset = haystack.find(new_needle, offset + 1)
    if found_any:
        return 253

    return 255

if __name__ == '__main__':
    sys.exit(main())
