# -*- coding: utf-8 -*-
#  libwordlist -- tools for generating wordlists
#  Copyright (C) 2017-2018  Uli Fouquet
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

"""libwordlist -- a library for wordlist-related operations.
"""
from __future__ import unicode_literals
try:
    from urllib.request import urlopen  # python 3.x
except ImportError:                     # pragma: no cover
    from urllib2 import urlopen         # python 2.x
try:
    from urllib.parse import urlparse   # python 3.x
except ImportError:                     # pragma: no cover
    from urlparse import urlparse       # python 2.x
import base64
import codecs
import logging
import os
import random
import re
import sys
import unicodedata
import zlib


DICE_SIDES = 6  #: we normally handle 6-sided dice.

#: The URL where the wordlists for Android are available.
BASE_URL_DICT_ANDROID = (
        "https//android.googlesource.com/platform/packages/inputmethods/"
        "LatinIME/+/master/dictionaries/")


#: A logger for use with diceware-list related messages.
logger = logging.getLogger("libwordlist")
logger.addHandler(logging.NullHandler())


def normalize(text):
    """Normalize text.
    """
    TRANSFORMS = {
        'ä': 'ae', 'Ä': 'AE', "æ": 'ae', "Æ": 'AE',
        'ö': 'oe', 'Ö': 'OE', "ø": 'oe', "Ø": 'OE',
        "ü": 'ue', "Ü": 'UE',
        'ß': 'ss', "Ð": 'D',
    }
    transformed = "".join([TRANSFORMS.get(x, x) for x in text])
    nfkd_form = unicodedata.normalize("NFKD", transformed)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def base10_to_n(num, base):
    """Turn base-10 integer `num` into base-`base` form.

    Returns a list of numbers representing digits in `base`.

    For instance in base-2 we have only the digits ``0`` and
    ``1``. Turning the base-10 integer ``5`` into a base-2 number
    results in ``101`` or, as a list, in::

        >>> base10_to_n(5, base=2)
        [1, 0, 1]

    The result list represents the single "digits" of a differently
    based number. This holds also for 'digits' >= 10::

        >>> base10_to_n(127, base=16)
        [7, 15]

    which in hexadecimal notation would normally read ``0x7F``.
    """
    result = []
    curr = num
    while curr >= base:
        curr, digit = divmod(curr, base)
        result.append(digit)
    result.append(curr)
    result.reverse()
    return result


def filter_chars(iter, allowed=None):
    """Yield strings from `iter` that contain only chars from `allowed`.

    If `allowed` is `None`, no filtering is done at all.
    """
    if allowed is None:
        for elem in iter:
            yield elem
    else:
        logger.info("Filtering out chars.")
        logger.debug("  Allowed chars: %r" % allowed)
        line = 0
        for elem in iter:
            line += 1
            stripped = [x for x in elem if x in allowed]
            if len(stripped) >= len(elem):
                yield elem
            else:
                logger.debug("  Not allowed char in line %d" % line)


def idx_to_dicenums(
        item_index, dice_num, dice_sides=DICE_SIDES, separator='-'):
    """Get a set of dicenums for list item numbers.

    Turn an index number of a list item into a number of dice numbers
    representing this index. The dicenums are returned as a string like
    ``"1-2-2-6-2-5"``.

    `item_index` is the index number of some item.

    `dice_num` is the number of (n-sided) dice used.

    `dice_sides` is the number of sides per die.

    `separator` is the string to separate the result numbers.

    Example: we have two dice resulting in 36 possible combinations. If
    first possible combination is "1-1", second one "1-2" and so on,
    then we have a mapping from indexes 1..36 to dice combinations (from
    "1-1" up to "6-6").

    For a reasonable result, we expect

      0 <= `item_index` < `dice_num` ** `dice_sides`.

    Some examples::

        >>> idx_to_dicenums(0, 1)
        '1'
        >>> idx_to_dicenums(5, 1)
        '6'
        >>> idx_to_dicenums(0, 3)
        '1-1-1'
        >>> idx_to_dicenums(5, 3)
        '1-1-6'

    We are not restricted to (6-sided) dice. If we throw a (2-sided)
    coin 3 times, we have an index range from ``0`` to ``2^3 = 8``
    (there are 8 possible combinations of coin throws). Index ``5``
    then computes to::

        >>> idx_to_dicenums(5, 3, 2)
        '2-1-2'

    If `dice_sides` < 10, you can generate compressed output by leaving
    the separator out::

        >>> idx_to_dicenums(5, 3, 2, separator="")
        '212'

    """
    nums = [x+1 for x in base10_to_n(item_index, dice_sides)]
    padded = [1, ] * dice_num + nums
    return separator.join(["%s" % x for x in padded[-dice_num:]])


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
    word_list = [x.strip() for x in word_list]
    if max_width is None:
        max_width = len(max(word_list, key=len))
    for entry in filter(lambda x: len(x) < max_width, word_list):
        yield entry
    max_width_entries = list(
        filter(lambda x: len(x) == max_width, word_list))
    random.shuffle(max_width_entries)
    for entry in max_width_entries:
        yield entry


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


def paths_iterator(paths):
    """Yield terms from files in `paths`.

    Each path is expected to be a readable, utf-8 encoded file containing
    terms, one per line.
    """
    for path in paths:
        if path == '-':
            for term in term_iterator([sys.stdin]):
                yield term
        else:
            with codecs.open(path, 'r', encoding='utf-8') as fd:
                for term in term_iterator([fd]):
                    yield term


def base_terms_iterator(use_kit=True, use_416=True):
    """Iterator over all base terms.

    Base terms are those conained in the diceware416 and dicewarekit
    lists.

    With `use_kit` and `use_416` you can tell whether these files should
    be used for generating lists or not.

    Terms are delivered encoded. This way we make sure, they have the
    same binary format as other terms read from files by `argparse`.
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

       >>> list(min_width_iter(["a", "ccc", "bb"], 2))
       ['a', 'bb']

    Please note that the iterator returned, delivers elements sorted by
    length first and terms of same length sorted alphabetically.

    """
    all_terms = sorted(iterator, key=lambda x: (len(x), x))
    if shuffle_max_width:
        max_width = len(all_terms[num - 1])
        all_terms = list(shuffle_max_width_items(all_terms, max_width))
    for term in all_terms[:num]:
        yield term


def is_prefix_code(iterable, is_sorted=False):
    """Tell whether a given list, identified by `iterable` is a prefix code.

    The prefix code is an attribute of lists, for which no element is
    prefix of another element in the list.

    We expect the elements of the list to be text/strings::

       >>> is_prefix_code(["a", "b", "c", "d"])
       True

       >>> is_prefix_code(["air", "airborn", "foo"])
       False

    If `is_sorted` is ``True``, we expect the iterable to be already
    sorted. If not, we will sort the list. Results are undefined for
    lists that are given as sorted, but are in fact not.

    """
    last_elem = None
    elems = iterable
    if not is_sorted:
        elems = sorted(iterable)
    for elem in elems:
        if last_elem and elem.startswith(last_elem):
            return False
        last_elem = elem
    return True


def get_matching_prefixes(iterable, is_sorted=False):
    """Get tuples of terms from `iterable` where one term is prefix of
    another term.

    The tuples will contain the prefix and exactly one prefixed term::

       >>> list(get_matching_prefixes(["a", "b", "aa"]))
       [('a', 'aa')]

    For terms that prefix more than one other term, one tuple is
    returned for each of the prefixed terms::

       >>> list(get_matching_prefixes(["a", "aa", "ab"]))
       [('a', 'aa'), ('a', 'ab')]

    The `is_sorted` parameter is a hint telling, whether the given
    `iterable` is already sorted or not. If it is, we do not resort
    the iterable and can compute results much faster.

    Results are undefined - and most probably broken -, if `is_sorted`
    is ``True`` while in fact the `iterable` is unsorted.

    This function is not destructive, which means that iterables
    passed-in will not be changed.

    """
    elems = iterable[:]
    if not is_sorted:
        elems.sort()
    while len(elems) > 1:
        idx = 1
        while elems[0] and elems[idx].startswith(elems[0]):
            yield elems[0], elems[idx]
            idx += 1
            if idx == len(elems):
                break
        elems.pop(0)


def strip_matching_prefixes(iterable, is_sorted=False, prefer_short=True):
    """Strip matching prefixes from `iterable`.

    Makes list in `iterable` a ``prefix code``. The returned iterator
    will be sorted.

    From pairs that share a prefix the alphabetically preceding one will
    remain in the result while the alphabetically "bigger" item will be
    discarded.

    This is a non-destructive operation. The passed-in iterable will
    not be changed.
    """
    elems = iterable[:]
    if not is_sorted:
        elems.sort()
    for elem in flatten_prefix_tree(
            get_prefixes(elems), prefer_short=prefer_short):
        yield elem


def get_prefixes(lst):
    """Get prefixes in sorted `lst`.

    The `lst` is expected to be a sorted wordlist.

    Return nested lists representing prefix structure of word list in `lst`. In
    this list all terms are put into lists of which the first one is the prefix
    of the following terms:

        ["a", "b", "c"]
        --> [["a"], ["b"], ["c"]]

        ["a", "aa", "ab"]
        --> [["a", ["aa"], ["ab"]]]

        ["a", "aa", "b", "ba", "baa", "c"]
        --> [["a", ["aa"]], ["b", ["ba", ["baa"]]], ["c"]]

    Apparently "a" is a prefix of "aa" and "ab" but "aa" and "ab" are not
    prefixes of some other word themselves.

    The nested lists can be read as binary trees:

     a          a      a
      \        /      / \
       b      aa     aa  b
        \      \        / \
         c     ab      ba  c
                       /
                     baa

    where left children of nodes are prefixed by the node itself, while right
    children are not.
    """
    stack = [[]]
    for item in lst + [""]:
        while len(stack) > 1:
            last = stack.pop()
            if item.startswith(last[0]):
                stack.append(last)
                break
            else:
                stack[-1].append(last)
        stack.append([item, ])
    return stack[0]


def flatten_prefix_tree(prefix_tree, prefer_short=True):
    """Turn a prefix tree into a simple list.

    Prefix trees are in fact nested lists as returned by
    `get_prefixes()`.

    The returned list will be prefix code, i.e. contain no term which is
    prefix of another.

    If 'prefer_short' is ``True`` and of two terms in the prefix tree
    one is the prefix of the other, the shorter one will be taken and
    the longer one discarded.

    Example::

       >>> flatten_prefix_tree([['a'], ['b'], ['c']])
       ['a', 'b', 'c']

    Normally, we pick the shorter one of two matching words::

       >>> flatten_prefix_tree([['a', ['ab']]])
       ['a']

    But we can tell to use the longer ones:

       >>> flatten_prefix_tree([['a', ['ab']]], prefer_short=False)
       ['ab']

    """
    result = []
    for elem in prefix_tree:
        if prefer_short or (len(elem) == 1):
            result.append(elem[0])
        else:
            result.extend(flatten_prefix_tree(elem[1:], prefer_short=False))
    return result


class AndroidWordList(object):
    """A wordlist provided for use in Android devices.

    The Android wordlists come as gzipped files and can be downloaded from
    internet.  They provide not only words we can use in diceware wordlists but
    also interesting meta infos about both, single words and whole lists
    provided.

    `AndroidWordList` objects provide methods to download and parse these
    lists.

    By default we use well-know URLs to download wordlists. But we also accept
    paths given at initialization.

    If language `lang` is set, use the respective language file when
    downloading.

    Android wordlists can be retrieved from source. There are different files
    for different languages, identified by 2-letter countrycodes like "en" for
    english or "de" for german.

    See::

        https://android.googlesource.com/platform/packages/inputmethods/
                LatinIME/+/master/dictionaries/

    for a complete list of available lists.

    If a `path` is given, we download the file on start-up. Otherwise, you have
    to call `download()` explicitly. Local files are expected to contain lists
    in gzipped format.

    If `path` is given, `lang` is ignored.

    Files once handled are stored in `gz_data`.
    """
    #: The URL where the wordlists for Android are available.
    base_url = (
            "https://android.googlesource.com/platform/packages/inputmethods/"
            "LatinIME/+/master/dictionaries/")

    #: The full download path to Android wordlists
    full_url = '%s%%s_wordlist.combined.gz?format=TEXT' % base_url

    def __init__(self, path=None, lang="en"):
        self.path = path
        self.gz_data = None
        self.lang = lang
        if self.path is not None:
            self.download()

    def download(self):
        """Download an android wordlist from upstream.

        The downloaded data is returned and stored in local `gz_data`
        attribute.
        """
        url = self.path
        if self.path is None:
            url = self.full_url % self.lang
        logger.info("Fetching wordlist from %s" % url)
        data = urlopen(url).read()
        if self.path is None:
            # the android `gitiles` repo provides files only base64 encoded.
            data = base64.b64decode(data)
        self.gz_data = data
        return self.gz_data

    def decompress(self, data):
        """Gunzip data in `data`.

        Returns the unzipped data.
        """
        # this is a dirty substitute for `gzip.decompress()` which
        # is not available in Python 2.x.
        return zlib.decompress(data, 16 + zlib.MAX_WBITS)

    def save(self, path):
        """Save downloaded wordlist to file `path`.

        If no wordlist file was downloaded before, nothing happens.

        Otherwise data is stored to `path`. Normally, this will be gzipped
        data, so a ``.gz`` filename extension in `path` would be appropriate.
        """
        if self.gz_data is None:
            return
        with open(path, 'wb') as f:
            f.write(self.gz_data)

    def get_basename(self, lang="en"):
        """Get basename of the file to download.
        """
        url = self.path
        if self.path is None:
            url = self.full_url % lang
        return os.path.basename(urlparse(url).path)

    def get_meta_data(self):
        """Return metadata for an Android wordlist as dict.

        Extracts metadata from regular Android wordlists, given in local
        `gz_data` attribute . If there is no data, the empty dict is returned.
        """
        for data_item in self.parse_lines():
            return data_item
        return {}

    def parse_lines(self):
        """Turn data from local word file list  in tuples of key-value pairs.

        Extracts data from local `gz_data`.

        Result is given as dict.

        Input data should be uncompressed file data from an Android wordlist.

        This method returns a generator.
        """
        if self.gz_data is not None:
            data = self.decompress(self.gz_data)
            for line in data.split(b'\n'):
                if not line:
                    continue  # ignore empty lines
                line = line.decode('utf-8')
                data = [tuple(x.strip().split('=')) for x in line.split(',')]
                yield dict(data)

    def get_words(self, offensive=None):
        """Get the basic words out of an Android word list.

        Android wordlists contain lots of meta data. This method returns only
        the words contained.

        Set `offensive` to `True` or `False` if you want only (`True`) or no
        (`False`) offensive words in your list. Any other value (including
        ``0``, ``1``, ``None``) ignores ``offensive`` flag of words.

        This method returns a generator.
        """
        for line in self.parse_lines():
            if 'word' not in line.keys():
                continue
            if 'possibly_offensive' in line.keys() and offensive is False:
                continue
            if 'possibly_offensive' not in line.keys() and offensive is True:
                continue
            yield line['word']

    def get_valid_lang_codes(self):
        """Get list of valid language codes from upstream.

        Fetches list of valid language codes from Android site.
        """
        resp = urlopen(self.base_url)
        html = resp.read()
        codes = [x.group(1).decode('utf-8') for x in
                 re.finditer(b'/([a-zA-Z_]+)_wordlist.combined.gz', html)]
        return sorted(codes)
