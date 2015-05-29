#!/usr/bin/python3


import argparse
import sys

from pattern import *


def int_bytes(n, le=True):
    bs = []
    while n > 0:
        bs.append(n % 0x100)
        n //= 0x100
    return bytes(bs) if le else bytes(reversed(bs))


def bytes_int(x, le=True):
    n = 0
    for b in reversed(needle) if le else needle:
        needle_int *= 0x100
        needle_int += b


def main(argv=None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument('needle',
                           help=('the pattern substring or hex value to '
                                 'search for'))
    argparser.add_argument('-s', '--needle-string', action='store_true',
                           help=('force interpretation of NEEDLE as a '
                                 'string rather than a hex value'))
    haystack_group = argparser.add_mutually_exclusive_group()
    haystack_group.add_argument('-f', '--haystack-file',
                                help=('the file containing the pattern to '
                                      'search'))
    haystack_group.add_argument('sets', nargs='*',
                                default=DEFAULT_PATTERN_SETS,
                                help=('the character sets from which the '
                                      'pattern was created'))
    argparser.add_argument('-l', '--length', type=int, default=None,
                           help='the length of the original pattern')
    argparser.add_argument('--fuzzy', action='store_true',
                           help='search for inexact matches')
    argparser.add_argument('-m', '--metasploit', action='store_true',
                           help=("attempt to emulate the output from MSF's "
                                 "'pattern_offset.rb' script.  "
                                 'Implies --fuzzy'))
    if argv is None:
        args = argparser.parse_args()
    else:
        args = argparser.parse_args(argv)

    # Try to guess whether we're looking at a byte string or hex digits.
    if args.needle_string or (len(args.needle) == 4 and
                              args.needle[:2] != '0x'):
        needle = args.needle.encode('utf-8')
        needle_int = bytes_int(needle)
    else:
        try:
            needle_digits = (args.needle[2:] if args.needle[:2] == '0x'
                             else args.needle)
            needle_int = int(needle_digits, 16)
            needle = int_bytes(needle_int)
        except ValueError:
            needle = args.needle.encode('utf-8')
            needle_int = bytes_int(needle)

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
        new_needle = bytes(reversed(needle))
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
                    mle = needle_int - bytes_int(new_needle)
                    mbe = needle_int - bytes_int(new_needle, le=False)
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
                new_needle = needle[:i] + bytes([c1, c2]) + needle[i + 2:]
                offset = haystack.find(new_needle)
                while offset != -1:
                    found_any = True
                    if args.metasploit:
                        mle = needle_int - bytes_int(new_needle)
                        mbe = needle_int - bytes_int(new_needle, le=False)
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
