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
import base64
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

    The file is gzipped, but not base64 encoded.
    """
    dictfile = tmpdir / "de_wordlist.combined.gz"
    src_path = os.path.join(
            os.path.dirname(__file__), "sample_short_wordlist_de.gz")
    shutil.copyfile(src_path, str(dictfile))
    return dictfile


@pytest.fixture
def dictfile_android_short_de_b64(request, tmpdir):
    """py.test fixture providing zipped, base64-encoded file.

    The file is gzipped and base64-encoded. Files downloaded from `gitiles` (as
    Android sources) come base64-encode. Annoying.
    """
    dictfile = tmpdir / "de_wordlist.combined.gz"
    src_path = os.path.join(
            os.path.dirname(__file__), "sample_short_wordlist_de.gz")
    dictfile.write(base64.b64encode(open(src_path, "rb").read()))
    return dictfile


@pytest.fixture
def local_android_download(request, monkeypatch, tmpdir):
    """py.test fixture provideing a AndroidWordList with local wordlist.
    """
    for lang in ['de', 'en']:
        dictfile = tmpdir / ("%s_wordlist.combined.gz" % lang)
        src_path = os.path.join(
                os.path.dirname(__file__), "sample_short_wordlist_%s.gz" % lang)
        dictfile.write(base64.b64encode(open(src_path, "rb").read()))
    fake_base_url = "file://%s/%%s_wordlist.combined.gz" % str(tmpdir)
    monkeypatch.setattr(
            "diceware_list.libwordlist.AndroidWordList.base_url",
            fake_base_url)
    return dictfile
