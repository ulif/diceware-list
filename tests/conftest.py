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
import logging
import os
import pytest
import shutil
import sys


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
def dictfile_android_short_en(request, tmpdir):
    """py.test fixture providing a short english android dict.

    The file is gzipped, but not base64 encoded.
    """
    dictfile = tmpdir / "en_wordlist.combined.gz"
    src_path = os.path.join(
            os.path.dirname(__file__), "sample_short_wordlist_en.gz")
    shutil.copyfile(src_path, str(dictfile))
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
def local_android_dir(request, tmpdir):
    """py.test fixture providing an AndroidWordList with local wordlists.

    Copies all local sample wordlists into a new tmpdir and returns the path to
    this dir.

    The files are not base64 encoded and the `AndroidWordList.base_url` stays
    untouched.

    For simulating file downloads from repository, use
    `local_android_download_b64` fixture below.
    """
    for lang in ['de', 'en']:
        dictfile = tmpdir / ("%s_wordlist.combined.gz" % lang)
        src_path = os.path.join(
            os.path.dirname(__file__), "sample_short_wordlist_%s.gz" % lang)
        shutil.copyfile(src_path, str(dictfile))
    return tmpdir


@pytest.fixture
def local_android_download_b64(request, monkeypatch, tmpdir):
    """py.test fixture providing an AndroidWordList with local wordlists.

    Copies all local sample wordlists into a new tmpdir. Then monkeypatches
    `AndroidWordList` to lookup wordlists right there and returns the temporary
    where all the wordlists reside.

    The files are stored base64-encoded, as this is, what the original google
    repos deliver.
    """
    for lang in ['de', 'en']:
        dictfile = tmpdir / ("%s_wordlist.combined.gz" % lang)
        src_path = os.path.join(
            os.path.dirname(__file__), "sample_short_wordlist_%s.gz" % lang)
        dictfile.write(base64.b64encode(open(src_path, "rb").read()))
    fake_base_url = "file://%s/" % str(tmpdir)
    index_html = open(
        os.path.join(os.path.dirname(__file__), 'sample_index.html')).read()
    tmpdir.join("index.html").write(index_html)
    monkeypatch.setattr(
            "diceware_list.libwordlist.AndroidWordList.base_url",
            fake_base_url)
    monkeypatch.setattr(
            "diceware_list.libwordlist.AndroidWordList.full_url",
            '%s%%s_wordlist.combined.gz' % fake_base_url)
    return tmpdir


@pytest.fixture
def local_index(request, monkeypatch, tmpdir):
    """This fixture provides a local copy of the Android download index

    The index page contains the links to all available language files and is
    used to compile a list of available labnguages.
    """
    index_html = open(
        os.path.join(os.path.dirname(__file__), 'sample_index.html')).read()
    tmpdir.join('index.html').write(index_html)
    monkeypatch.setattr(
            "diceware_list.libwordlist.AndroidWordList.base_url",
            'file://%s/index.html' % str(tmpdir))
    return tmpdir


@pytest.fixture(scope="function")
def home_dir(request, monkeypatch, tmpdir):
    """This fixture provides a temporary user home.

    During run the user is changed to the temporary home dir.
    """
    tmpdir.mkdir("home")
    monkeypatch.setenv("HOME", str(tmpdir / "home"))
    path = tmpdir / "home"
    path.chdir()
    return path


@pytest.fixture(scope="function", autouse=True)
def teardown_loggers():
    """This fixture will remove any lingering loghandlers after test.

    The `yield` syntax is a shortcut to define setup and teardown code.
    """
    yield "will-remove-lingering-loghandlers"
    logger = logging.getLogger("libwordlist")
    for handler in logger.handlers:
        logger.removeHandler(handler)
        logger.setLevel(logging.NOTSET)


@pytest.fixture(scope="function")
def argv_handler(request):
    """This fixture restores sys.argv and sys.stdin after tests.
    """
    _argv_stored = sys.argv
    _stdin_stored = sys.stdin

    def teardown():
        sys.argv = _argv_stored
        sys.stdin = _stdin_stored
    request.addfinalizer(teardown)
