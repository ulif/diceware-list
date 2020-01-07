# -*- coding: utf-8 -*-
#  diceware-list -- generate wordlists for diceware
#  Copyright (C) 2017,2018 Uli Fouquet
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
"""Tests for wlflakes module.
"""
from __future__ import unicode_literals
import pytest
import sys
from diceware_list import __version__
from diceware_list.wlflakes import (
    find_flakes, get_cmdline_args, main, check_E1, check_E2, check_E3,
    check_W1
)


class TestArgParser(object):

    def test_sys_argv_as_fallback(self, monkeypatch, capfd, dictfile):
        # if we deliver no args, `sys.argv` is used.
        monkeypatch.setattr(sys, "argv", ["scriptname", str(dictfile)])
        get_cmdline_args()
        out, err = capfd.readouterr()
        assert err == ""

    def test_wordlist_file_required(self, capfd):
        # we require at least one argument, a wordlist file
        with pytest.raises(SystemExit) as why:
            get_cmdline_args(None)
        assert why.value.args[0] == 2
        out, err = capfd.readouterr()
        if sys.version_info < (3, 0):
            assert "too few arguments" in err
        else:
            assert "the following arguments are required" in err

    def test_wordlist_file_must_exist(self, capfd):
        # we require at least one argument, a wordlist file
        with pytest.raises(SystemExit):
            get_cmdline_args(["foobar", ])
        out, err = capfd.readouterr()
        assert ("No such file or directory: " in err)
        assert ("'foobar'" in err)

    def test_version(self, capfd):
        # we can output current version.
        with pytest.raises(SystemExit):
            get_cmdline_args(["--version", ])
        out, err = capfd.readouterr()
        assert __version__ in (out + err)


class TestFindFlakes(object):

    def test_noflakes(self, capfd, tmpdir):
        # a flawless wordlist will produce no output
        wordlist = tmpdir / "mywordlist.txt"
        wordlist.write("bar\nbaz\nfoo\n")
        find_flakes([open(str(wordlist)), ])
        out, err = capfd.readouterr()
        assert out == ''
        assert err == ''

    def test_can_find_prefixes(self, capfd, dictfile, tmpdir):
        # we can find prefixes
        wordlist = tmpdir / "mywordlist.txt"
        wordlist.write("bar\nbarfoo\nbaz\n")
        with open(str(wordlist)) as fd:
            find_flakes([fd, ], prefixes=True)
        out, err = capfd.readouterr()
        assert (
            'mywordlist.txt:2: E1 "bar" from line 1 is a '
            'prefix of "barfoo"') in out

    def test_can_find_doubles(self, capfd, dictfile, tmpdir):
        # we can identify double terms
        wordlist = tmpdir / "wordlist.txt"
        wordlist.write("bar\nfoo\nbar\n")
        with open(str(wordlist)) as fd:
            find_flakes([fd, ], prefixes=False)
        out, err = capfd.readouterr()
        assert(
            'wordlist.txt:1: E2 "bar" appears multiple times' in out)

    def test_detect_too_short_terms(self, capfd, dictfile, tmpdir):
        # we can find out if a term is too short
        wordlist = tmpdir / "wordlist.txt"
        wordlist.write("a\nbb\naaa\n")
        with open(str(wordlist)) as fd:
            find_flakes([fd, ], prefixes=False)
        out, err = capfd.readouterr()
        assert(
            'wordlist.txt:1: E3 "a" is too short.' in out)


class TestCheckers(object):

    def test_E1(self):
        # we can determine whether a list represents a prefix code
        assert list(check_E1(["foo", "bar"])) == []
        assert list(check_E1(["foo", "foobar"])) == [
            '2: E1 "foo" from line 1 is a prefix of "foobar"']

    def test_E1_counts_lines_correctly(self):
        # check_E1 can count lines
        assert list(check_E1(["foo", "bar", "barbaz"])) == [
            '3: E1 "bar" from line 2 is a prefix of "barbaz"']
        assert list(check_E1(["foo", "barbaz", "bar"])) == [
            '2: E1 "bar" from line 3 is a prefix of "barbaz"']

    def test_E1_copes_with_umlauts(self):
        # E1 works with terms containing non-ASCII chars.
        assert list(check_E1(["foo", "bärbaz", "bär"])) == [
            '2: E1 "bär" from line 3 is a prefix of "bärbaz"']

    def test_E2(self):
        # we can check whether a list contains double elements
        assert list(check_E2(["foo", "bar"])) == []
        assert list(check_E2(["foo", "foo"])) == [
            '1: E2 "foo" appears multiple times']

    def test_E2_copes_with_umlauts(self):
        # E2 works with terms containing umlauts
        assert list(check_E2(["für", "für", "far"])) == [
            '1: E2 "für" appears multiple times']

    def test_E3(self):
        # we detect too short terms
        assert list(check_E3(['a', 'bb', 'aaa'])) == [
            '1: E3 "a" is too short. Minimum length should be 2.']

    def test_W1(self):
        # we can detect terms containing non-ASCII chars
        assert list(check_W1([b"foo", b"bar"])) == []
        assert list(
            check_W1(["für".encode("utf-8"), "bar".encode("utf-8")])) == [
                '1: W1 "für" contains non-ASCII chars']

    def test_W1_unicode_input(self):
        # we cope with unicode input
        assert list(check_W1(["foo", "bar"])) == []
        assert list(
            check_W1(["für", "bar"])) == [
                '1: W1 "für" contains non-ASCII chars']


class TestMain(object):

    def test_main(self, monkeypatch):
        # we can call the main function (although it will require extra args)
        monkeypatch.setattr(sys, "argv", ["scriptname", ])
        with pytest.raises(SystemExit):
            main()

    def test_can_get_help(self, monkeypatch, capfd):
        # we can get help
        monkeypatch.setattr(sys, "argv", ["scriptname", "--help"])
        with pytest.raises(SystemExit):
            main()
        out, err = capfd.readouterr()
        assert "show this help message" in out

    def test_can_run_main(self, monkeypatch, capfd, dictfile, tmpdir):
        # we can run wlflakes.
        wordlist = tmpdir / "mywordlist.txt"
        wordlist.write("bar\nfoo\nbaz\n")
        monkeypatch.setattr(sys, "argv", ["scriptname", str(wordlist)])
        main()
        out, err = capfd.readouterr()
        assert out == ""
        assert err == ""
