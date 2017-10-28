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


class TestArgParser(object):

    def test_version(self, monkeypatch, capfd):
        # we can output current version.
        with pytest.raises(SystemExit):
            get_cmdline_args(["--version", ])
        out, err = capfd.readouterr()
        assert __version__ in (out + err)


class TestMain(object):

    def test_main(self, monkeypatch, capfd):
        # we can call the main function
        monkeypatch.setattr(sys, "argv", ["scriptname", ])
        main()
        out, err = capfd.readouterr()
        assert out == ""

    def test_can_get_help(self, monkeypatch, capfd, home_dir):
        # we can get help
        monkeypatch.setattr(sys, "argv", ["scriptname", "--help"])
        with pytest.raises(SystemExit):
            main()
        out, err = capfd.readouterr()
        assert "show this help message" in out
