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
import imp
import os
import pytest
import sys
from wlflakes import get_cmdline_args


def test_main_script_runnable(capfd, monkeypatch):
    # we can really run the wlflakes script
    monkeypatch.setattr(sys, "argv", ["scriptname", "--help"])
    script_loc = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'wlflakes.py')
    with pytest.raises(SystemExit) as exc_info:
        imp.load_source('__main__', script_loc)
    out, err = capfd.readouterr()
    assert out.startswith("usage: ")
    assert exc_info.value.code == 0

class TestArgParser(object):

    def test_sys_argv_as_fallback(self, monkeypatch, capfd):
        # if we deliver no args, `sys.argv` is used.
        monkeypatch.setattr(sys, "argv", ["scriptname"])
        get_cmdline_args()
        out, err = capfd.readouterr()
        assert err == ""
