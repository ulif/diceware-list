# -*- coding: utf-8 -*-
#  wlflakes -- check wordlist for flakes
#  Copyright (C) 2017  Uli Fouquet
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
from diceware_list.libwordlist import get_matching_prefixes, term_iterator


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
        for msg in check_E1(terms):
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


def main():
    """Main function for `wlflakes` script.
    """
    args = get_cmdline_args()
    find_flakes(args.wordlistfile)
