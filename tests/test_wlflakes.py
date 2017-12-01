# -*- coding: utf-8 -*-
#  diceware-list -- generate wordlists for diceware
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
"""Tests for wlflakes module.
"""
import pytest
import sys
from diceware_list import __version__
from diceware_list.wlflakes import (
        find_flakes, get_cmdline_args, main, check_E1
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
        assert "No such file or directory: 'foobar'" in err

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
