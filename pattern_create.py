#!/usr/bin/python3


import sys
import argparse
from itertools import islice, cycle

from pattern import *


def main(argv=None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument('length', type=int)
    argparser.add_argument('sets', nargs='*', default=DEFAULT_PATTERN_SETS)
    argparser.add_argument('--width', type=int, default=4)
    argparser.add_argument('--force-permutations', action='store_true')
    if argv is None:
        args = argparser.parse_args()
    else:
        args = argparser.parse_args(argv)

    try:
        print(''.join(pattern_create(args.length, args.sets, args.width)))
    except NotEnoughPermutationsError as e:
        if args.force_permutations:
            print(''.join(islice(cycle(weave(args.sets)), args.length)))
        else:
            print(e, file=sys.stderr)
            return 2
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
