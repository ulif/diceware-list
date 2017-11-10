# -*- coding: utf-8 -*-
#  diceware_list -- generate wordlists for diceware
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

# Tests for wldownload module
from __future__ import unicode_literals
import pytest
import sys
from diceware_list import __version__
from diceware_list.wldownload import (
        download_wordlist, get_cmdline_args, main
        )


def test_download_wordlist(home_dir, local_android_download_b64):
    # we can download wordlists
    download_path = home_dir / "en_wordlist.combined.gz"
    download_wordlist()
    assert download_path.exists()


class TestArgParser(object):

    def test_version(self, monkeypatch, capfd):
        # we can output current version.
        with pytest.raises(SystemExit):
            get_cmdline_args(["--version", ])
        out, err = capfd.readouterr()
        assert __version__ in (out + err)

    def test_verbose(self):
        # we can require verbosity
        args = get_cmdline_args([])
        assert args.verbose is None
        args = get_cmdline_args(["-v", ])
        assert args.verbose == 1
        args = get_cmdline_args(["--verbose", ])
        assert args.verbose == 1
        args = get_cmdline_args(["-vv", ])
        assert args.verbose == 2


class TestMain(object):

    def test_main(
            self, monkeypatch, local_android_download_b64, home_dir):
        # we can call the main function
        download_path = home_dir / "en_wordlist.combined.gz"
        monkeypatch.setattr(sys, "argv", ["scriiptname", ])
        main()
        assert download_path.exists()

    def test_can_get_help(self, monkeypatch, capfd, home_dir):
        # we can get help
        monkeypatch.setattr(sys, "argv", ["scriptname", "--help"])
        with pytest.raises(SystemExit):
            main()
        out, err = capfd.readouterr()
        assert "show this help message" in out

    def test_main_no_verbose(
            self, monkeypatch, local_android_download_b64, home_dir, capfd):
        # by default we do not output anything
        monkeypatch.setattr(sys, "argv", ["scriptname", ])
        main()
        out, err = capfd.readouterr()
        assert out == ""
        assert err == ""

    def test_main_verbose(
            self, monkeypatch, local_android_download_b64, home_dir, capfd):
        # in verbose mode, we tell at least what we do
        monkeypatch.setattr(sys, "argv", ["scriptname", "-v"])
        main()
        out, err = capfd.readouterr()
        assert out == ""
        assert err != ""
        assert "Basename" not in err

    def test_main_verbose_increased(
            self, monkeypatch, local_android_download_b64, home_dir, capfd):
        # we can be more verbose
        monkeypatch.setattr(sys, "argv", ["scriptname", "-vv"])
        main()
        out, err = capfd.readouterr()
        assert out == ""
        assert "Basename" in err

    def test_main_existing_file_errors(
            self, monkeypatch, local_android_download_b64, home_dir, capfd):
        # we do not overwrite existing target files
        monkeypatch.setattr(sys, "argv", ["scriptname", ])
        download_path = home_dir / "en_wordlist.combined.gz"
        download_path.write("foo")
        with pytest.raises(SystemExit):
            main()
        out, err = capfd.readouterr()
        assert "File exists" in err
        assert download_path.read() == "foo"  # original file unchanged
