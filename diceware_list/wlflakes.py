# -*- coding: utf-8 -*-
#  wlflakes -- check wordlist for flakes
#  Copyright (C) 2017, 2018 Uli Fouquet
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
"""wlflakes -- CLI to find flakes in diceware wordlists.
"""
from __future__ import unicode_literals
import argparse
from diceware_list import __version__
from diceware_list.libwordlist import (
    get_matching_prefixes, term_iterator, min_len
)


def get_cmdline_args(args=None):
    """Handle commandline options for `wlflakes`.
    """
    parser = argparse.ArgumentParser(
        description="Find flakes in diceware wordlists")
    parser.add_argument(
        'wordlistfile', nargs='+', metavar='FILE', default=None,
        type=argparse.FileType('r'),
        help=("Wordlist file to read possible terms from. "
              "Multiple allowed. `-' will read from stdin."),
    )
    parser.add_argument(
        '--ignore-prefix', action='store_true',
        help='Ignore terms being a prefix of other terms'),
    parser.add_argument(
        '-v', '--verbose', action='count', help='be verbose.')
    parser.add_argument(
        '--version', action='version', version=__version__,
        help='output version information and exit.')
    return parser.parse_args(args)


def find_flakes(file_descriptors, prefixes=True):
    """Check all `file_descriptors` for problems.

    Each file descriptor must be open for reading.
    """
    for descriptor in file_descriptors:
        filename = descriptor.name
        terms = list(term_iterator([descriptor]))
        for checker in check_E1, check_E2, check_W1:
            for msg in checker(terms):
                print('%s:%s' % (filename, msg))


def check_E1(terms):
    """Check if list in `terms` is a prefix code.

    `terms` must be a list of terms.

    Yields messages, each one representing an E1 violation.
    """
    double_prefixes = get_matching_prefixes(terms, is_sorted=False)
    for t1, t2 in double_prefixes:
        i1, i2 = terms.index(t1), terms.index(t2)
        msg = '%d: E1 "%s" from line %d is a prefix of "%s"' % (
            i2 + 1, t1, i1 + 1, t2)
        yield msg


def check_E2(terms):
    """Check if terms in `terms` appear two or more times.

    `terms` must be a list of terms.

    Yields messages, each one representing an E1 violation.
    """
    last = None
    for term in sorted(terms):
        if last is not None:
            if last == term:
                msg = '%d: E2 "%s" appears multiple times' % (
                    terms.index(term) + 1, term)
                yield msg
        last = term

def check_E3(terms):
    """Check, whether there are too short terms contained.

    `terms` mus be a list of terms.

    Yields a message if the shortest terms can easier be bruteforced than
    guessed by combining terms.
    """
    required_len = min_len(terms)
    for n, t in enumerate(terms):
        if len(t) < required_len:
            msg = '%d: E3 "%s" is too short. Minimum length should be %s.' % (
                n + 1, t, int(required_len))
            yield msg


def check_W1(terms):
    """Check if terms contain non-ASCII chars.

    terms must be a list of terms

    Yields message, wach on representing an W1 violation.
    """
    for n, t in enumerate(terms):
        if hasattr(t, 'encode') and not hasattr(t, "decode"):
            t = t.encode("utf-8")
        try:
            t.decode('ascii')
        except(UnicodeDecodeError):
            msg = '%d: W1 "%s" contains non-ASCII chars' % (
                n + 1, t.decode('utf-8'))
            yield msg
        except(UnicodeEncodeError):  # pragma: nocover
            msg = '%d: W1 "%s" contains non-ASCII chars' % (
                n + 1, t)
            yield msg


def main():
    """Main function for `wlflakes` script.
    """
    args = get_cmdline_args()
    find_flakes(args.wordlistfile)
