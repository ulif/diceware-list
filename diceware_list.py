# -*- coding: utf-8 -*-
#  diceware_list -- generate wordlists for diceware
#  Copyright (C) 2016  Uli Fouquet
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""diceware_list -- wordlists for diceware.
"""
import argparse
import math
import os
import string

DICE_SIDES = 6  # we normally handle 6-sided dice.
DEFAULT_CHARS = string.ascii_letters + string.digits + string.punctuation


def get_cmdline_args(args=None):
    """Handle commandline options.
    """
    parser = argparse.ArgumentParser(description="Create a wordlist")
    parser.add_argument(
        '-l', '--length', default=8192, type=int, dest='length',
        help='desired length of generated wordlist. Default: 8192')
    parser.add_argument(
        '-n', '--numbered', action='store_true',
        help='show dicenumbers in output.')
    parser.add_argument(
        '--ascii', action='store_true', dest='ascii_only',
        help='allow only words that contain only ASCII chars.')
    parser.add_argument(
        '-k', '--no-kit', action='store_false', dest='use_kit',
        help='do not include the "dicewarekit" list from diceware.com.')
    parser.add_argument(
        '--use-416', action='store_true',
        help='use terms from diceware416.txt list.')
    parser.add_argument(
        'dictfile', nargs='+', metavar='DICTFILE',
        type=argparse.FileType('r'),
        help=("Dictionary file to read possible terms from. "
              "Multiple allowed. `-' will read from stdin."),
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='be verbose.')
    return parser.parse_args(args)


def base10_to_n(num, base):
    """Turn base-10 integer `num` into base-`base` form.

    Returns a list of numbers representing digits in `base`.
    """
    result = []
    curr = num
    while curr >= base:
        curr, digit = divmod(curr, base)
        result.append(digit)
    result.append(curr)
    result.reverse()
    return result


def idx_to_dicenums(item_index, dice_num):
    """Get a set of dicenums for list item numbers.

    Turn an index number of a list item into a number of dice numbers
    representing this index. The dicenums are returned as a string like
    ``"122625"``.

    `item_index` is the index number of some item.

    `dice_num` is the number of (six-sided) dice used.

    Example: we have two dice resulting in 36 possible combinations. If
    first possible combination is "1-1", second one "1-2" and so on,
    then we have a mapping from indexes 1..36 to dice combinations (from
    "1-1" up to "6-6").

    For a reasonable result, we expect 0 >= `item_index` < `dice_num`**6.
    """
    nums = [x+1 for x in base10_to_n(item_index, DICE_SIDES)]
    padded = [1, ] * dice_num + nums
    return "".join(["%s" % x for x in padded[-dice_num:]])


def min_width_iter(iterator, num):
    """Get an iterable with `num` elements and minimal 'list width' from
    items in `iterator`.

    If 'list width' is the sum of length of all items contained in a
    list or iterable, then `min_list_width` generates an iterator over
    `num` elements in this list/iterable, which results in a list with
    minimal 'list width'.

    For instance, for a list ['a', 'bb', 'ccc'] the list width would be
    1 + 2 + 3 = 6. For ['a', 'bbb'] this would be 1 + 3 = 4. If we want
    to build a minimum width version from the former list with two
    elements, these elements had to be 'a' and 'bb' (resulting in a list
    width of 3). All other combinations of two elements of the list
    would result in list widths > 3.

    Please note that the iterator returned, delivers elements sorted by
    length first and terms of same length sorted alphabetically.

    """
    all_terms = sorted(iterator, key=lambda x: (len(x), x))
    for term in all_terms[:num]:
        yield term


def filter_chars(iter, allowed=None):
    """Yield strings from `iter` that contain only chars from `allowed`.

    If `allowed` is `None`, no filtering is done at all.
    """
    if allowed is None:
        for elem in iter:
            yield elem
    else:
        for elem in iter:
            stripped = [x for x in elem if x in allowed]
            if len(stripped) == len(elem):
                yield elem


def generate_wordlist(
        input_terms, length=8192, lowercase=True, use_kit=True,
        use_416=False, numbered=False, ascii_only=False):
    """Generate a diceware wordlist from dictionary list.

    `input_terms`: iterable over all strings to consider as wordlist item.

    `length`: desired length of wordlist to generate.

    `lowercase`: yield terms lowercase if set.

    `use_kit`: add terms from "dicewarekit", a wordlist with basic terms
               provided by Arnold G. Reinhold for self-baked diceware
               wordlists.

    `use_416`: add terms from another wordlist of Mr Reinhold,
               containing 416 terms.

    `ascii_only`: only accept words, that exclusively contain ASCII.

    Returns an iterator that yields at most `length` items. Double
    entries are removed.
    """
    if ascii_only:
        input_terms = filter_chars(input_terms, allowed=DEFAULT_CHARS)
    base_terms = list(base_terms_iterator(use_kit=use_kit, use_416=use_416))
    terms = list(set(list(input_terms) + list(base_terms)))
    terms.sort()
    if len(terms) < length:
        raise ValueError(
            "Wordlist too short: at least %s unique terms required." % length)
    if length:
        dicenum = int(math.ceil(math.log(length) / math.log(DICE_SIDES)))
    prefix = ""
    for num, term in enumerate(sorted(min_width_iter(terms, length))):
        if lowercase:
            term = term.lower()
        if numbered:
            prefix = idx_to_dicenums(num, dicenum) + " "
        yield "%s%s" % (prefix, term)


def term_iterator(file_descriptors):
    """Yield terms from files in `file_descriptors`.

    Empty lines are ignored.

    `file_descriptors` must be open for reading.
    """
    for fd in file_descriptors:
        for term in fd:
            term = term.strip()
            if term:
                yield term


def base_terms_iterator(use_kit=True, use_416=True):
    """Iterator over all base terms.

    Base terms are those conained in the diceware416 and dicewarekit
    lists.

    With `use_kit` and `use_416` you can tell whether these files should
    be used for generating lists or not.

    Terms are delivered encoded. This way we make sure, they have the
    same binary format as oter terms read from files by `argparse`.
    """
    names = []
    if use_kit:
        names += ["dicewarekit.txt", ]
    if use_416:
        names += ["diceware416.txt"]
    dir_path = os.path.join(os.path.dirname(__file__))
    fd_list = [open(os.path.join(dir_path, name), "r") for name in names]
    for term in term_iterator(fd_list):
        yield term


def main():
    """Main function of script.

    Output the wordlist determined by commandline args.
    """
    args = get_cmdline_args()
    all_terms = term_iterator(args.dictfile)
    for term in generate_wordlist(
            all_terms, args.length, use_kit=args.use_kit,
            use_416=args.use_416, numbered=args.numbered,
            ascii_only=args.ascii_only):
        print(term)


if __name__ == "__main__":
    main()
