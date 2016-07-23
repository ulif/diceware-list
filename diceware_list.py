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
import logging
import math
import os
import random
import string
import unicodedata

DICE_SIDES = 6  # we normally handle 6-sided dice.
DEFAULT_CHARS = string.ascii_letters + string.digits + string.punctuation

#: A logger for use with diceware-list related messages.
logger = logging.getLogger("ulif.diceware-list")
logger.addHandler(logging.NullHandler())


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
        '-s', '--sides', default=6, type=int,
        help='assume used dice have SIDES sides. Default: 6')
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
        '-v', '--verbose', action='count',
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


def idx_to_dicenums(item_index, dice_num, dice_sides=DICE_SIDES):
    """Get a set of dicenums for list item numbers.

    Turn an index number of a list item into a number of dice numbers
    representing this index. The dicenums are returned as a string like
    ``"122625"``.

    `item_index` is the index number of some item.

    `dice_num` is the number of (n-sided) dice used.

    `dice_sides` is the number of sides per die.

    Example: we have two dice resulting in 36 possible combinations. If
    first possible combination is "1-1", second one "1-2" and so on,
    then we have a mapping from indexes 1..36 to dice combinations (from
    "1-1" up to "6-6").

    For a reasonable result, we expect

      0 <= `item_index` < `dice_num` ** `dice_sides`.

    """
    nums = [x+1 for x in base10_to_n(item_index, dice_sides)]
    padded = [1, ] * dice_num + nums
    return "".join(["%s" % x for x in padded[-dice_num:]])


def min_width_iter(iterator, num, shuffle_max_width=True):
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
    if shuffle_max_width:
        max_width = len(all_terms[num - 1])
        all_terms = list(shuffle_max_width_items(all_terms, max_width))
    for term in all_terms[:num]:
        yield term


def shuffle_max_width_items(word_list, max_width=None):
    """Shuffle entries of `word_list` that have max width.

    Yields items in `word_list` in preserved order, but with maximum
    width entries shuffled. This helps to create lists, that have only
    entries with minimal width but a random set of maximum width
    entries.

    For instance::

      ["a", "b", "aa", "bb", "aaa", "bbb", "ccc"]

    could end up::

      ["a", "b", "aa", "bb", "ccc", "aaa", "bbb"]


    That means the three maximum-width elements at the end are returned
    in different order.
    """
    if max_width is None:
        max_width = len(max(word_list, key=len))
    for entry in filter(lambda x: len(x) < max_width, word_list):
        yield entry
    max_width_entries = list(
        filter(lambda x: len(x) == max_width, word_list))
    random.shuffle(max_width_entries)
    for entry in max_width_entries:
        yield entry


def normalize(text):
    """Normalize text.
    """
    TRANSFORMS = {
        u'ä': u'ae', u'Ä': u'AE', u"æ": u'ae', u"Æ": u'AE',
        u'ö': u'oe', u'Ö': u'OE', u"ø": u'oe', u"Ø": u'OE',
        u"ü": u'UE', u"Ü": u'UE',
        u'ß': u'ss'
    }
    transformed = u"".join([TRANSFORMS.get(x, x) for x in text])
    nfkd_form = unicodedata.normalize("NFKD", transformed)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def filter_chars(iter, allowed=None):
    """Yield strings from `iter` that contain only chars from `allowed`.

    If `allowed` is `None`, no filtering is done at all.
    """
    if allowed is None:
        for elem in iter:
            yield elem
    else:
        logger.info("Filtering out chars not in: %s" % allowed)
        for elem in iter:
            stripped = [x for x in elem if x in allowed]
            if len(stripped) >= len(elem):
                yield elem
            else:
                logger.debug("  Contains not allowed chars: %s" % elem)


def generate_wordlist(
        input_terms, length=8192, lowercase=True, use_kit=True,
        use_416=False, numbered=False, ascii_only=False,
        shuffle_max=True, dice_sides=DICE_SIDES):
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

    `shuffle_max`: shuffle max width entries before cutting and sorting.
               This way a random set of max width entries gets included
               instead of the same fixed set at the beginning of all max width
               entries. I.e. not only those max width entries starting with
               ``a`` or ``b`` are included, but instead (randomly) also ``x``,
               ``y``, ``z`` might appear. By default we shuffle entries. Set
               to `False` to avoid this.

    `dice_sides`: number of sides of dice exepected to be used with the
               result list. This is important only if the output list is
               numbered. By default we expect six sides.

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
        dicenum = int(math.ceil(math.log(length) / math.log(dice_sides)))
    prefix = ""
    for num, term in enumerate(sorted(min_width_iter(
            terms, length, shuffle_max))):
        if lowercase:
            term = term.lower()
        if numbered:
            prefix = idx_to_dicenums(num, dicenum, dice_sides=dice_sides) + " "
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
        logger.debug("Adding source list: dicewarekit.txt")
        names += ["dicewarekit.txt", ]
    if use_416:
        logger.debug("Adding source list: diceware416.txt")
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
    if args.verbose:
        logger.setLevel(logging.INFO)
        if args.verbose > 1:
            logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        logger.debug("Verbose logging enabled")
        logger.info("Creating wordlist...")
    for term in generate_wordlist(
            all_terms, args.length, use_kit=args.use_kit,
            use_416=args.use_416, numbered=args.numbered,
            ascii_only=args.ascii_only, dice_sides=args.sides):
        print(term)


if __name__ == "__main__":
    main()
