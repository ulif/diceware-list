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
#
"""py.test config for `diceware-list` modules.
"""
import os
import pytest
import shutil


@pytest.fixture
def dictfile(request, tmpdir):
    """py.test fixture providing a dictfile.

    The returned file is a py.local instance.

    The entries in here are mainy like ``zzz0``...``zzz8192``.
    This is not a prefix code.
    """
    dictfile = tmpdir / "dictfile.txt"
    contents = "\n".join(["zzz%s" % x for x in range(8192)])
    dictfile.write("foo\nbar\n" + contents)
    return dictfile


@pytest.fixture
def dictfile_ext(request, tmpdir):
    """py.test fixture providing a dictfile which is prefix code.

    The returned file is a py.local instance. Different from the other
    `dictfile`, this one is nearly a prefix code, except the both entries
    ``zzz0000`` and ``zzz00000``.
    """
    dictfile = tmpdir / "dictfile.txt"
    contents = "\n".join(["zzz%04d" % x for x in range(8192)])
    dictfile.write("a\nbb\nbbb\nc\n" + contents)
    return dictfile


@pytest.fixture
def dictfile_android_short_de(request, tmpdir):
    """py.test fixture providing a short (2 terms) android dict.
    """
    dictfile = tmpdir / "de_wordlist.combined.gz"
    src_path = os.path.join(
            os.path.dirname(__file__), "sample_short_wordlist_de.gz")
    shutil.copyfile(src_path, str(dictfile))
    return dictfile
