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
import pkg_resources
import string
from libwordlist import (
    DICE_SIDES, base_terms_iterator, filter_chars, idx_to_dicenums, logger,
    min_width_iter, term_iterator,
)

__version__ = pkg_resources.get_distribution('diceware-list').version


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
        '-d', '--sides', default=6, type=int,
        help='assume used dice have SIDES sides. Default: 6')
    parser.add_argument(
        '-k', '--use-kit', action='store_true', dest='use_kit',
        help='include the "dicewarekit" list from diceware.com.')
    parser.add_argument(
        '--use-416', action='store_true',
        help='use terms from diceware416.txt list.')
    parser.add_argument(
        'dictfile', nargs='*', metavar='DICTFILE', default=None,
        type=argparse.FileType('r'),
        help=("Dictionary file to read possible terms from. "
              "Multiple allowed. `-' will read from stdin."),
    )
    parser.add_argument(
        '-v', '--verbose', action='count',
        help='be verbose.')
    parser.add_argument(
        '--version', action='store_true',
        help='output version information and exit.')
    return parser.parse_args(args)


def generate_wordlist(
        input_terms, length=8192, lowercase=True, use_kit=False,
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
    if length and numbered:
        dicenum = int(math.ceil(math.log(length) / math.log(dice_sides)))
    prefix = ""
    for num, term in enumerate(sorted(min_width_iter(
            terms, length, shuffle_max))):
        if lowercase:
            term = term.lower()
        if numbered:
            prefix = idx_to_dicenums(num, dicenum, dice_sides) + " "
        yield "%s%s" % (prefix, term)


def main():
    """Main function of script.

    Output the wordlist determined by commandline args.
    """
    args = get_cmdline_args()
    if args.version:
        print(__version__)
        raise SystemExit(0)

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
