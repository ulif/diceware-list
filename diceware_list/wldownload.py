# -*- coding: utf-8 -*-
#  wldownload -- download and mangle remote wordlists
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
""" wldownload -- CLI to download and mangle remote wordlists.
"""
from __future__ import unicode_literals
import argparse
from diceware_list import __version__
from diceware_list.libwordlist import AndroidWordList


def get_cmdline_args(args=None):
    """Handle commandline options for `wldownload`.
    """
    parser = argparse.ArgumentParser(
        description="Download and mangle remote wordlists")
    parser.add_argument(
        '-v', '--verbose', action='count', help='be verbose.')
    parser.add_argument(
        '--version', action='version', version=__version__,
        help='output version information and exit.')
    return parser.parse_args(args)


def download_wordlist():
    """Download and mangle remote wordlists.
    """
    pass


def main():
    """Main function for `wldownload` script.
    """
    args = get_cmdline_args()
    download_wordlist()
