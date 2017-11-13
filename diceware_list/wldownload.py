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
import logging
import os
import sys
from diceware_list import __version__
from diceware_list.libwordlist import AndroidWordList, logger


def get_cmdline_args(args=None):
    """Handle commandline options for `wldownload`.
    """
    parser = argparse.ArgumentParser(
        description="Download and mangle Android wordlists")
    parser.add_argument(
        '-o', '--outfile', action='store', help='file to store output.')
    parser.add_argument(
        '-v', '--verbose', action='count', help='be verbose.')
    parser.add_argument(
        '--version', action='version', version=__version__,
        help='output version information and exit.')
    return parser.parse_args(args)


def get_save_path(word_list, outfile=None):
    """Compute a path, where to store wordlist files.

    The `word_list` must be an `AndroidWordList` or something similar, that
    provides a `get_basename` method.

    The `outfile` is a path or filename normally given by users.

    The returned path will be normalized and all that.
    """
    if outfile is None:
        result = os.path.join(os.getcwd(), word_list.get_basename())
    else:
        result = os.path.abspath(outfile)
    return result


def download_wordlist(verbose=None, outfile=None):
    """Download and mangle remote wordlists.
    """
    wl = AndroidWordList()
    basename = outfile or wl.get_basename()
    if os.path.exists(basename):
        logger.error("cannot create '%s': File exists" % basename)
        sys.exit(73)  # 73 is the EX_CANTCREAT exit code
    logger.info("Starting download of Android wordlist file.")
    wl.download()
    logger.debug("Download finished. Basename: %s" % wl.get_basename())
    wl.save(basename)
    logger.info("Done.")


def main():
    """Main function for `wldownload` script.
    """
    args = get_cmdline_args()
    logger.setLevel(logging.WARNING)
    if args.verbose:
        logger.setLevel(logging.INFO)
        if args.verbose > 1:
            logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    download_wordlist(verbose=args.verbose)
