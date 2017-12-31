# -*- coding: utf-8 -*-
#  diceware_list -- generate wordlists for diceware
#  Copyright (C) 2016-2017.  Uli Fouquet
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

# Tests for libwordlist module
from __future__ import unicode_literals
try:
    from urllib.request import urlopen, URLError  # python 3.x
except ImportError:                               # pragma: no cover
    from urllib2 import urlopen, URLError         # python 2.x
from io import StringIO
import codecs
import gzip
import random
import pytest
import sys
from diceware_list import DEFAULT_CHARS
from diceware_list.libwordlist import (
    base10_to_n, filter_chars, base_terms_iterator, idx_to_dicenums,
    min_width_iter, normalize, shuffle_max_width_items, term_iterator,
    paths_iterator, is_prefix_code, get_matching_prefixes, get_prefixes,
    strip_matching_prefixes, flatten_prefix_tree, AndroidWordList
    )


EMPTY_GZ_FILE = (
    b'\x1f\x8b\x08\x08\xea\xc1\xecY\x02\xffsample_emtpy'
    b'\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00')


def ggsource_unreachable():
    """Check, whether we can ping android.googlesource.com'.

    Respective tests may be skipped if no network is available.
    """
    try:
        urlopen('https://android.googlesource.com/').read()
    except URLError:
        return True
    return False


def test_base10_to_n():
    # we can turn integers into n-based numbers
    assert base10_to_n(0, 2) == [0]
    assert base10_to_n(1, 2) == [1]
    assert base10_to_n(2, 2) == [1, 0]
    assert base10_to_n(3, 2) == [1, 1]
    assert base10_to_n(7775, 6) == [5, 5, 5, 5, 5]
    assert base10_to_n(0, 6) == [0, ]
    assert base10_to_n(1, 6) == [1, ]
    assert base10_to_n(6, 6) == [1, 0]
    assert base10_to_n(34, 6) == [5, 4]
    assert base10_to_n(35, 6) == [5, 5]
    assert base10_to_n(37, 6) == [1, 0, 1]
    assert base10_to_n(38, 6) == [1, 0, 2]
    assert base10_to_n(255, 16) == [15, 15]
    assert base10_to_n(256, 16) == [1, 0, 0]


def test_filter_chars():
    # we can detect words with unwanted chars
    assert list(filter_chars([], DEFAULT_CHARS)) == []
    assert list(filter_chars(["a", "b"], DEFAULT_CHARS)) == ["a", "b"]
    assert list(filter_chars(["ä"], DEFAULT_CHARS)) == []
    assert list(filter_chars(["a", "ä"], DEFAULT_CHARS)) == ["a"]
    assert list(filter_chars(["ä", "a"], DEFAULT_CHARS)) == ["a"]
    assert list(filter_chars(["a", "ä", "b"], DEFAULT_CHARS)) == ["a", "b"]
    assert list(filter_chars(["a", "aä", "bö"], DEFAULT_CHARS)) == ["a"]
    assert list(filter_chars([u"a", u"ä"], DEFAULT_CHARS)) == [u"a"]


def test_filter_chars_all_allowed():
    # if `allowed` is None, no filtering will be done
    assert list(filter_chars(['ä'], None)) == ['ä']


def test_idx_to_dicenums():
    # we can get dice numbers from list indexes
    assert idx_to_dicenums(0, 5) == "1-1-1-1-1"
    assert idx_to_dicenums(1, 5) == "1-1-1-1-2"
    assert idx_to_dicenums(7774, 5) == "6-6-6-6-5"
    assert idx_to_dicenums(7775, 5) == "6-6-6-6-6"
    # different dice sides, different results
    assert idx_to_dicenums(0, 4, 4) == "1-1-1-1"
    assert idx_to_dicenums(255, 4, 4) == "4-4-4-4"
    assert idx_to_dicenums(255, 4) == "2-2-1-4"
    # we can change the separator string (or leave it out)
    assert idx_to_dicenums(0, 3) == "1-1-1"  # default
    assert idx_to_dicenums(0, 3, separator="sep") == "1sep1sep1"
    assert idx_to_dicenums(0, 3, separator="") == "111"


def test_idx_to_dicenums_gives_text():
    # we get text from this function, i.e. unicode under py2.
    result = idx_to_dicenums(0, 5)
    assert isinstance(result, type('text'))


def test_min_width_iter(monkeypatch):
    # we can get iterators with minimal list width.
    monkeypatch.setattr(random, "shuffle", lambda x: x)
    assert list(min_width_iter(["bb", "a", "ccc", "dd"], 3)) == [
        "a", "bb", "dd"]
    assert list(min_width_iter(["c", "a", "b"], 2)) == ["a", "b"]
    assert list(min_width_iter(["c", "a", "b"], 3)) == ["a", "b", "c"]
    assert list(min_width_iter(["a", "c", "bb"], 2)) == ["a", "c"]
    assert list(min_width_iter(["a", "cc", "b"], 2)) == ["a", "b"]
    assert list(min_width_iter(["aa", "c", "bb"], 2)) == ["c", "aa"]


def test_min_width_iter_shuffle_max_widths_values(monkeypatch):
    # words with maximum width are shuffled
    monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
    assert list(min_width_iter(
        ["a", "aa", "bb"], 2, shuffle_max_width=True)) == ["a", "bb"]
    assert list(min_width_iter(
        ["bbb", "aa", "a"], 2, shuffle_max_width=True)) == ["a", "aa"]
    assert list(min_width_iter(
        ["aa", "a"], 2, shuffle_max_width=True)) == ["a", "aa"]


def test_normalize():
    # we can normalize texts.
    assert normalize("ªºÀÁÂÃÄÅÆ") == "aoAAAAAEAAE"
    assert normalize("ÇÈÉÊËÌÍÎÏ") == "CEEEEIIII"
    assert normalize("ÒÓÔÕÖØÙÚÛÜ") == "OOOOOEOEUUUUE"
    assert normalize("ÐÑÝßàáâãäåæçèéêë") == "DNYssaaaaaeaaeceeee"
    assert normalize("ìíîïñòóôõöøùúûüý") == "iiiinoooooeoeuuuuey"
    # "þÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİ"
    # "ıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖŗŘřŚśŜŝŞşŠšŢţ"
    # "ŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽžſƀƁƂƃƄƅƆƇƈƉƊƋƌƍ"
    assert normalize("mäßig") == "maessig"


def test_normalize_gives_text():
    # we get unicode/text strings back
    assert isinstance(normalize("far"), type("text"))
    assert isinstance(normalize("fär"), type("text"))
    assert isinstance(normalize(str("far")), type("text"))


def test_shuffle_max_width_items(monkeypatch):
    # we can shuffle the max width items of a list
    # install a pseudo-shuffler that generates predictable orders
    # so that last elements are returned in reverse order.
    monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
    # an ordered list
    result = list(shuffle_max_width_items(["a", "aa", "bb", "cc"]))
    assert result == ["a", "cc", "bb", "aa"]
    # an unordered list
    result = list(shuffle_max_width_items(["aa", "d", "bb", "a", "cc"]))
    assert result == ["d", "a", "cc", "bb", "aa"]
    # a list of which the longes item should not be part of
    result = list(shuffle_max_width_items(
        ["eeee", "bb", "ccc", "aa", "ddd"], max_width=3))
    assert "eeee" not in result
    # a list with one length only
    result = list(shuffle_max_width_items(["aa", "bb", "cc"]))
    assert result == ["cc", "bb", "aa"]


def test_shuffle_max_width_items_copes_with_files(monkeypatch, tmpdir):
    # when shuffling max width entries we accept file input
    monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
    wlist = tmpdir.join("wlist.txt")
    wlist.write(b"\n".join([b"a", b"bb", b"cc"]))
    with open(str(wlist), "rb") as fd:
        result = list(shuffle_max_width_items(fd))
    assert result == [b"a", b"cc", b"bb"]


def test_base_terms_iterator():
    # we can get an iterator over base terms
    base_iter = base_terms_iterator()
    base_list = list(base_iter)
    assert "a2" in base_list
    assert "9z" in base_list
    assert "0" in base_list
    assert "zzzz" in base_list


def test_base_terms_iterator_option_use_kit():
    # we can tell whether to use dicewarekit, diceware416 lists.
    assert "yyyy" not in list(base_terms_iterator(use_kit=False))
    assert "a2" in list(base_terms_iterator(use_kit=False))
    assert "yyyy" in list(base_terms_iterator(use_kit=True))
    assert "a2" in list(base_terms_iterator(use_kit=True))


class TestTermIterator(object):

    def test_term_iterator(self, tmpdir):
        # the term_iterator really returns iterators
        wlist = tmpdir.join("wlist.txt")
        wlist.write(b"\n".join([b"a", b"b", b"c"]))
        with open(str(wlist), "rb") as fd:
            result = list(term_iterator([fd, ]))
        assert result == [b"a", b"b", b"c"]

    def test_term_iterator_multiple_files(self, tmpdir):
        # we can feed multiple input files to term_iterator
        wlist1 = tmpdir.join("wlist1.txt")
        wlist2 = tmpdir.join("wlist2.txt")
        wlist1.write(b"\n".join([b"a1", b"b1", b"c1"]))
        wlist2.write(b"\n".join([b"a2", b"b2", b"c2"]))
        with open(str(wlist1), "rb") as fd1:
            with open(str(wlist2), "rb") as fd2:
                result = list(term_iterator([fd1, fd2]))
        assert result == [b"a1", b"b1", b"c1", b"a2", b"b2", b"c2"]

    def test_term_iterator_handles_umlauts(self, tmpdir):
        # we can feed term iterators with umlauts
        wlist = tmpdir.join("wlist.txt")
        wlist.write_text(u"ä\nö\n", "utf-8")
        with codecs.open(str(wlist), "r", "utf-8") as fd:
            result = list(term_iterator([fd, ]))
        assert result == ["ä", "ö"]

    def test_term_iterator_ignores_empty_lines(self, tmpdir):
        # empty lines will be ignored
        wlist = tmpdir.join("wlist.txt")
        wlist.write("foo\n\nbar\n\n")
        with open(str(wlist), "r") as fd:
            result = list(term_iterator([fd, ]))
        assert result == ["foo", "bar"]


class TestPathsIterator(object):

    def test_paths_iterator(self, tmpdir):
        # the paths iterator provides terms from paths
        wlist = tmpdir.join("wlist.txt")
        wlist.write(b"\n".join([b"a", b"b", b"c"]))
        result = list(paths_iterator([str(wlist), ]))
        assert result == ["a", "b", "c"]

    def test_multiple_paths(self, tmpdir):
        # the paths iterator can cope with several files
        wlist1 = tmpdir.join("wlist1.txt")
        wlist2 = tmpdir.join("wlits2.txt")
        wlist1.write(b"a\nb")
        wlist2.write(b"c\nd")
        result = list(paths_iterator([str(wlist1), str(wlist2)]))
        assert result == ["a", "b", "c", "d"]

    def test_read_stdin(self, tmpdir, argv_handler):
        # we can tell to read from stdin (dash as filename)
        sys.stdin = StringIO('term1\nterm2\näöü\n')
        result = list(paths_iterator('-'))
        assert result == ['term1', 'term2', 'äöü']


class TestIsPrefixCode(object):

    def test_is_prefix_code(self):
        # we can really tell whether some list is a prefix code.
        assert is_prefix_code(["aa", "ab", "ac"]) is True
        assert is_prefix_code([]) is True
        assert is_prefix_code(["a", "ab", "c"]) is False
        assert is_prefix_code(["a", "c", "ab"]) is False
        assert is_prefix_code(["aa", "b", "a"]) is False  # order
        assert is_prefix_code(["a", "a"]) is False        # identity

    def test_is_prefix_code_sorted_input(self):
        # we do not sort already sorted input
        assert is_prefix_code(["a", "aa", "b"], is_sorted=True) is False
        assert is_prefix_code(["b", "c", "d"], is_sorted=True) is True
        assert is_prefix_code(["b", "a"], is_sorted=False) is True
        # we do not define behavior for unsorted lists, if `is_sorted` is True

    def test_is_prefix_code_accepts_iter(self):
        # is_prefix_code really copes with iterators (not only iterables)
        assert is_prefix_code(iter(["a", "b", "c"])) is True
        assert is_prefix_code(iter(["aa", "a"])) is False

    def test_is_prefix_code_non_destructive(self):
        # is_prefix_code is a non-destructive function.
        iterable = ["d", "b", "c"]
        is_prefix_code(iterable, is_sorted=False)
        assert iterable == ["d", "b", "c"]
        iterable = ["a", "b", "c"]
        is_prefix_code(iterable, is_sorted=True)
        assert iterable == ["a", "b", "c"]

    def test_is_prefix_code_non_ascii(self):
        # is_prefix_code copes with umlauts etc.
        assert is_prefix_code(["z", "ä", "y", "äh"]) is False
        assert is_prefix_code(["a", "äh"]) is True


class TestGetMatchingPrefixes(object):

    def test_get_matching_prefixes(self):
        assert list(get_matching_prefixes([])) == []
        assert list(get_matching_prefixes(["a", "aa", "ab", "b", "x"])) == [
            ("a", "aa"), ("a", "ab")]
        assert list(get_matching_prefixes(["a", "aa"])) == [("a", "aa")]
        assert list(get_matching_prefixes(["b", "aa", "a"])) == [("a", "aa")]

    def test_get_matching_prefixes_sorted_input(self):
        # we can presort input lists
        assert list(
            get_matching_prefixes(["a", "aa", "ab"], is_sorted=True)) == [
            ("a", "aa"), ("a", "ab")]
        assert list(get_matching_prefixes(["aa", "a"], is_sorted=False)) == [
            ("a", "aa")]
        assert list(
            get_matching_prefixes(["a", "aa", "aaa"], is_sorted=True)) == [
                ("a", "aa"), ("a", "aaa"), ("aa", "aaa")]
        assert list(
            get_matching_prefixes(["a", "aa", "aaa", "aaaa"], is_sorted=True)
            ) == [
                    ("a", "aa"), ("a", "aaa"), ("a", "aaaa"), ("aa", "aaa"),
                    ("aa", "aaaa"), ("aaa", "aaaa")]

    def test_get_matching_prefixes_non_destructive(self):
        # the given input will not be changed.
        iterable = ["a", "aa", "c"]
        list(get_matching_prefixes(iterable, is_sorted=False))
        assert iterable == ["a", "aa", "c"]
        list(get_matching_prefixes(iterable, is_sorted=True))
        assert iterable == ["a", "aa", "c"]

    def test_get_matching_prefixes_non_ascii(self):
        # get_matching_prefixes copes with umlauts etc.
        get_matching_prefixes(["a", "ä", "ö"], is_sorted=False) == []
        get_matching_prefixes(["a", "ä", "äh"], is_sorted=False) == [
            ("ä", "äh")]


class TestStrinMatchingPrefixes(object):

    def test_strip_matching_prefixes(self):
        # we can get prefix code from any input
        assert list(strip_matching_prefixes(
            ["a", "aa", "b"], is_sorted=False, prefer_short=True)
            ) == ["a", "b"]
        assert list(strip_matching_prefixes(
            ["aa", "a", "b"], is_sorted=False, prefer_short=True)
            ) == ["a", "b"]
        assert list(strip_matching_prefixes(
            ["a", "aa"], is_sorted=False, prefer_short=True)) == ["a"]
        assert list(strip_matching_prefixes(
            ["aa", "a"], is_sorted=False, prefer_short=True)) == ["a"]

    def test_strip_matching_prefixes_empty(self):
        # we cope with empty iterables
        assert list(strip_matching_prefixes([], is_sorted=True)) == []

    def test_strip_matching_prefixes_non_destructive(self):
        # given input will not be modified
        in_list = ["b", "a", "aa"]
        result = list(strip_matching_prefixes(in_list, is_sorted=False))
        assert in_list == ["b", "a", "aa"]  # unchanged
        assert result == ["a", "b"]

    def test_strip_matching_prefixes_prefer_short(self):
        # we can tell to prefer shorter prefixes
        in_list = ["a", "aa", "b"]
        result1 = list(strip_matching_prefixes(
            in_list, is_sorted=False, prefer_short=True))
        assert result1 == ["a", "b"]
        result2 = list(strip_matching_prefixes(
            in_list, is_sorted=False, prefer_short=False))
        assert result2 == ["aa", "b"]
        result3 = list(strip_matching_prefixes(
            ["a", "aa", "ab", "c"], is_sorted=True, prefer_short=True))
        assert result3 == ["a", "c"]

    def test_strip_matching_prefixes_third_nesting_level(self):
        #  we cope with highly nested prefixes
        result = list(strip_matching_prefixes(
            ["a", "aa", "aaa"], prefer_short=False))
        assert result == ["aaa"]
        result = list(strip_matching_prefixes(
            ["a", "aa", "aaa"], prefer_short=True))
        assert result == ["a"]


def test_get_prefixes():
    # we can create tree-like nested lists of prefixed lists of strings
    assert get_prefixes([]) == []
    assert get_prefixes(["a"]) == [["a"]]
    assert get_prefixes(["a", "b"]) == [["a"], ["b"]]
    assert get_prefixes(["a", "ab"]) == [["a", ["ab"]]]
    assert get_prefixes(["a", "aa", "b"]) == [["a", ["aa"]], ["b"]]
    assert get_prefixes(["a", "b", "ba"]) == [["a"], ["b", ["ba"]]]
    assert get_prefixes(["a", "aa", "aaa", "ab"]) == [
        ['a', ['aa', ['aaa']], ['ab']]]
    assert get_prefixes(["a", "aa", "aaa", "ab", "ac"]) == [
        ['a', ['aa', ['aaa']], ['ab'], ['ac']]]


def test_flatten_prefix_tree():
    # we can flatten prefix trees
    assert flatten_prefix_tree([["a"], ["b"]]) == ["a", "b"]
    assert flatten_prefix_tree([["a", ["ab"]]]) == ["a"]
    assert flatten_prefix_tree(
        [["a", ["ab"]]], prefer_short=False) == ["ab"]
    assert flatten_prefix_tree(
        [['a', ['aa', ['aaa']], ['ab'], ['ac']]], prefer_short=False) == [
            'aaa', 'ab', 'ac']


class TestAndroidWordlist(object):

    def test_attributes(self):
        # android wordlists objects provide some attributes we expect
        wl = AndroidWordList()
        assert hasattr(wl, "base_url")
        assert hasattr(wl, "path")
        assert hasattr(wl, "gz_data")
        assert hasattr(wl, "lang")

    def test_init_path(self, local_android_dir):
        # we can pass in a path to an unencoded file (no base64).
        path = local_android_dir / "de_wordlist.combined.gz"
        wl = AndroidWordList('file:////%s' % path)
        assert wl.path == 'file:////%s' % path

    def test_download(self, local_android_download_b64):
        # we can download wordfiles that are base64 encoded.
        wl = AndroidWordList(lang="de")
        dl_data = wl.download()
        assert wl.decompress(dl_data) == (
            b'dictionary=main:de,locale=de,description=Deutsch,'
            b'date=1414726263,version=54,REQUIRES_GERMAN_UMLAUT_PROCESSING=1'
            b'\n word=der,f=216,flags=,originalFreq=216\n word=und,f=213,'
            b'flags=,originalFreq=213\n')

    def test_download_de(self, local_android_download_b64):
        # we can download a german wordlist.
        wl = AndroidWordList(lang="de")
        wl.download()
        assert list(wl.get_words()) == ['der', 'und']

    def test_download_en(self, local_android_download_b64):
        # we can download an english wordlist.
        wl = AndroidWordList(lang="en")
        wl.download()
        assert list(wl.get_words()) == [
            'the', 'to', 'of', 'and', 'hardcore', 'import']

    def test_decompress(self, local_android_dir):
        # we can decompress downloaded stuff.
        wl = AndroidWordList()
        path = local_android_dir / "de_wordlist.combined.gz"
        data = path.read_binary()
        assert wl.decompress(data).startswith(b"dictionary=main:de,locale=de")

    def test_save(self, local_android_download_b64, tmpdir):
        # we can save downloaded wordlists.
        wl = AndroidWordList(lang="en")
        wl.download()
        path = tmpdir / 'mywordlist.gz'
        wl.save(str(path))
        assert path.isfile()
        assert path.size() == 235

    def test_save_no_data(self, local_android_download_b64, tmpdir):
        # we do not complain when no data was downloaded already
        wl = AndroidWordList()
        path = tmpdir / 'mywordlist.gz'
        wl.save(str(path))
        assert not path.isfile()

    def test_get_basename(self):
        # we can get the basename of the file to download
        wl = AndroidWordList()
        assert wl.get_basename() == "en_wordlist.combined.gz"

    def test_get_basename_lang(self, local_android_download_b64):
        # when getting basename, we can select the language
        wl = AndroidWordList()
        assert wl.get_basename(lang="de") == "de_wordlist.combined.gz"

    def test_get_basename_path(self, local_android_dir):
        # we get a correct basename also if path is set manually
        wl = AndroidWordList()
        path1 = local_android_dir / "de_wordlist.combined.gz"
        path2 = local_android_dir / "my_wordlist.gzip"
        path1.copy(path2)
        wl = AndroidWordList('file:////%s' % path2)
        assert wl.get_basename(lang="foo") == "my_wordlist.gzip"

    def test_metadata(self, local_android_dir):
        # we can extract metadata from android wordfiles
        path = local_android_dir / "de_wordlist.combined.gz"
        wl = AndroidWordList()
        wl.gz_data = path.read_binary()
        meta = wl.get_meta_data()
        assert meta == {
                'dictionary': 'main:de',
                'locale': 'de',
                'description': 'Deutsch',
                'date': '1414726263',
                'version': '54',
                'REQUIRES_GERMAN_UMLAUT_PROCESSING': '1'
        }

    def test_metadata_none(self):
        # we cope with situation, when no wordfile was set before.
        wl = AndroidWordList()
        assert wl.get_meta_data() == {}

    def test_metadata_empty(self):
        # we cope with situation, where the wordfile is empty
        wl = AndroidWordList()
        wl.gz_data = EMPTY_GZ_FILE
        assert wl.get_meta_data() == {}

    def test_parse_lines(self, local_android_dir):
        # we can raw parse simple lists
        path = local_android_dir / "de_wordlist.combined.gz"
        wl = AndroidWordList('file:////%s' % path)
        lines = wl.parse_lines()
        assert [x for x in lines] == [
            {
                'dictionary': 'main:de',
                'locale': 'de',
                'description': 'Deutsch',
                'date': '1414726263',
                'version': '54',
                'REQUIRES_GERMAN_UMLAUT_PROCESSING': '1'},
            {
                'word': 'der', 'f': '216', 'flags': '',
                'originalFreq': '216'},
            {
                'word': 'und', 'f': '213', 'flags': '',
                'originalFreq': '213'},
        ]

    def test_parse_lines_ignores_empty_lines(self, tmpdir):
        # empty lines in wordlist files are ignored by the parser
        path = tmpdir / 'sample_empty_lines.gz'
        with gzip.open(str(path), 'wb') as f:
            f.write(b'\n\n\n')
        wl = AndroidWordList('file:////%s' % path)
        lines = wl.parse_lines()
        assert list(lines) == []

    def test_get_words(self, dictfile_android_short_de):
        # we can get plain wordlists from Android lists
        wl = AndroidWordList("file:////%s" % str(dictfile_android_short_de))
        assert [x for x in wl.get_words()] == ["der", "und"]

    def test_get_words_offensive(self, dictfile_android_short_en):
        # we can filter out offensive words
        wl = AndroidWordList("file:////%s" % str(dictfile_android_short_en))
        list1 = list(wl.get_words(offensive=False))
        assert "hardcore" not in list1
        assert "the" in list1
        list2 = list(wl.get_words(offensive=True))
        assert "hardcore" in list2
        assert "the" not in list2
        list3 = list(wl.get_words(offensive=None))
        assert "hardcore" in list3
        assert "the" in list3

    @pytest.mark.skipif(ggsource_unreachable(), reason="no network available")
    def test_get_valid_lang_codes(self):
        # we can get a list of available language codes.
        wl = AndroidWordList()
        result = wl.get_valid_lang_codes()
        assert result[0:3] == ['cs', 'da', 'de']

    def test_get_valid_lang_codes_local(self, local_index):
        # get valid lang codes from local copy of index list.
        wl = AndroidWordList()
        result = wl.get_valid_lang_codes()
        assert result == [
                'cs', 'da', 'de', 'el', 'en', 'en_GB', 'en_US', 'es',
                'fi', 'fr', 'hr', 'it', 'iw', 'lt', 'lv', 'nb', 'nl', 'pl',
                'pt_BR', 'pt_PT', 'ro', 'ru', 'sl', 'sr', 'sv', 'tr']
