#  wordlist_gen -- generate wordlists for diceware
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
"""wordlist_gen -- wordlists for diceware.
"""
import argparse
import os


def get_cmdline_args(args=None):
    """Handle commandline options.
    """
    parser = argparse.ArgumentParser(description="Create a wordlist")
    parser.add_argument(
        '-l', '--length', default=8192, type=int, dest='length',
        help='desired length of generated wordlist. Default: 8192')
    parser.add_argument(
        'dictfile', nargs='+', metavar='DICTFILE',
        type=argparse.FileType('rb'),
        help=("Dictionary file to read possible terms from. "
              "Multiple allowed. `-' will read from stdin."),
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='be verbose.')
    return parser.parse_args(args)


def filtered_by_len(iterator, min_len=3, max_len=None):
    """Get an iterator over words from `iterator`.

    Only words of len `min_len`..`max_len` are included.

    The lines we find (and that meet our requirements) are yielded.
    """
    for line in iterator:
        line = line.strip()
        if (len(line) < min_len) or (max_len and len(line) > max_len):
            continue
        yield line


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


def generate_wordlist(input_terms, length=8192, lowercase=True):
    """Generate a diceware wordlist from dictionary list.

    `input_terms`: iterable over all strings to consider as wordlist item.

    `length`: desired length of wordlist to generate.

    `lowercase`: yield terms lowercase if set.

    Returns an iterator that yields at most `length` items. Double
    entries are removed.
    """
    base_terms = list(base_terms_iterator(use_kit=False, use_416=False))
    terms = list(set(list(input_terms) + list(base_terms)))
    terms.sort()
    if len(terms) < length:
        raise ValueError(
            "Wordlist too short: at least %s unique terms required." % length)
    for term in sorted(min_width_iter(terms, length)):
        if lowercase:
            term = term.lower()
        yield term


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
    fd_list = [open(os.path.join(dir_path, name), "rb") for name in names]
    for term in term_iterator(fd_list):
        yield term


def main():
    """Main function of script.

    Output the wordlist determined by commandline args.
    """
    args = get_cmdline_args()
    all_terms = term_iterator(args.dictfile)
    for term in generate_wordlist(all_terms, args.length):
        print(term.decode("utf-8"))


if __name__ == "__main__":
    main()
