import string
from fractions import gcd
from itertools import islice, cycle, chain, product
from functools import reduce
import operator


DEFAULT_PATTERN_SETS = [string.ascii_uppercase, string.ascii_lowercase,
                        string.digits]


def weave(sets):
    """
    Interweave character sets together, ensuring that no duplicates
    between character sets exist.
    """
    if not sets:
        raise ValueError('no sets')
    union = set()
    for s in sets:
        sset = set(s)
        if len(sset) != len(s):
            raise ValueError('duplicate item in set')
        if not union.isdisjoint(sset):
            raise ValueError('intersecting sets')
        union |= sset

    return chain.from_iterable(product(*sets))


class NotEnoughPermutationsError(ValueError):
    def __init__(self, max_items):
        super(NotEnoughPermutationsError, self).__init__(
            'not enough permutations for more than {} items'.format(max_items))


def pattern_create(length=None, sets=DEFAULT_PATTERN_SETS,
                   allow_repeats=False):
    """
    Create a pattern guaranteed not to contain repeats.

    If the requested length is too long, a NotEnoughPermutationsError is
    raised.

    Arguments:
    length -- the length of the pattern.  If None, defaults to the
              greatest length possible without repeats.
    sets -- the character sets from which to construct the pattern
    allow_repeats -- whether repeats are allowed
    """
    if length is not None and length < 0:
        raise ValueError('length cannot be negative')
    if length == 0:
        return []

    num_unique_blocks = reduce(operator.mul, (len(s) for s in sets))
    unique_block_items = num_unique_blocks * len(sets)
    max_items = unique_block_items
    if length is None:
        length = max_items
    elif length > max_items and not allow_repeats:
        raise NotEnoughPermutationsError(max_items)

    return islice(cycle(weave(sets)), length)


__all__ = ['DEFAULT_PATTERN_SETS', 'weave', 'NotEnoughPermutationsError',
           'pattern_create']
