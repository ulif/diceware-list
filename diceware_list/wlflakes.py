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


def get_cmdline_args(args=None):
    """Handle commandline options for `wlflakes`.
    """
    parser = argparse.ArgumentParser(
        description="Find flakes in diceware wordlists")
    parser.add_argument(
        '-v', '--verbose', action='count', help='be verbose.')
    return parser.parse_args(args)


def main():                                                  # pragma: no cover
    """Main function for `wlflakes` script.
    """
    get_cmdline_args()


if __name__ == '__main__':                                   # pragma: no cover
    main()
