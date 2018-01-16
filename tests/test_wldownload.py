# -*- coding: utf-8 -*-
#  diceware_list -- generate wordlists for diceware
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

# Tests for wldownload module
from __future__ import unicode_literals
import pytest
import sys
from diceware_list import __version__
from diceware_list.libwordlist import AndroidWordList
from diceware_list.wldownload import (
        download_wordlist, get_save_path, get_cmdline_args, main
        )


def test_get_save_path(home_dir):
    # we can clearly determine a path to store data
    wl = AndroidWordList()
    assert get_save_path(wl) == str(home_dir / "en_wordlist.combined.gz")
    wl = AndroidWordList()
    assert get_save_path(wl, outfile="foo") == str(home_dir / "foo")


class TestDowmloadWordlist(object):

    def test_download_wordlist(
            self, home_dir, local_android_download_b64, capfd):
        # we can download wordlists
        download_wordlist()
        out, err = capfd.readouterr()
        assert len(out) > 0

    def test_download_wordlist_respects_lang(
            self, home_dir, local_android_download_b64, capfd):
        # we respect the given `lang`
        download_wordlist(lang="de")
        out, err = capfd.readouterr()
        assert out == "der\nund\n"

    def test_download_wordlist_respects_filter_offensive(
            self, home_dir, local_android_download_b64, capfd):
        # we respect the given `filter_offensive` flag
        download_wordlist(filter_offensive=True)
        out, err = capfd.readouterr()
        assert "hardcore" not in out

    def test_download_wordlist_respects_filter_offensive_false(
            self, home_dir, local_android_download_b64, capfd):
        # we respect the given `filter_offensive` flag if ``False``
        download_wordlist(filter_offensive=False)
        out, err = capfd.readouterr()
        assert "hardcore" in out

    def test_download_wordlist_respects_filter_offensive_none(
            self, home_dir, local_android_download_b64, capfd):
        # we respect the given `filter_offensive` flag if ``None``
        download_wordlist(filter_offensive=None)
        out, err = capfd.readouterr()
        assert "hardcore" in out


class TestArgParser(object):

    def test_version(self, capfd):
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

    def test_outfile(self, capfd):
        # we can set an output path
        args = get_cmdline_args([])
        assert args.outfile is None
        args = get_cmdline_args(["-o", "foo", ])
        assert args.outfile == "foo"
        args = get_cmdline_args(["--outfile", "bar", ])
        assert args.outfile == "bar"
        with pytest.raises(SystemExit):
            # the path should not be empty
            get_cmdline_args(["-o", ])
        out, err = capfd.readouterr()
        assert "expected one argument" in err

    def test_raw(self):
        # we can request raw output
        args = get_cmdline_args([])
        assert args.raw is False
        args = get_cmdline_args(['--raw', ])
        assert args.raw is True

    def test_lang(self):
        # we can request a certain language
        args = get_cmdline_args([])
        assert args.lang == 'en'
        args = get_cmdline_args(['--lang', 'de'])
        assert args.lang == 'de'
        args = get_cmdline_args(['-l', 'fr'])
        assert args.lang == 'fr'

    def test_lang_codes(self):
        # we can ask for a list of valid lang codes
        args = get_cmdline_args([])
        assert args.lang_codes is False
        args = get_cmdline_args(['--lang-codes'])
        assert args.lang_codes is True


class TestMain(object):

    def test_main(
            self, monkeypatch, local_android_download_b64, capfd):
        # we can call the main function
        monkeypatch.setattr(sys, "argv", ["scriiptname", ])
        main()
        out, err = capfd.readouterr()
        assert out.startswith("the\nto\nof\n")
        assert "hardcore" in out

    def test_can_get_help(self, monkeypatch, capfd, home_dir):
        # we can get help
        monkeypatch.setattr(sys, "argv", ["scriptname", "--help"])
        with pytest.raises(SystemExit):
            main()
        out, err = capfd.readouterr()
        assert "show this help message" in out

    def test_main_no_verbose(
            self, monkeypatch, local_android_download_b64, home_dir, capfd):
        # by default we do not save any files.
        monkeypatch.setattr(sys, "argv", ["scriptname", ])
        main()
        out, err = capfd.readouterr()
        assert out != ""
        assert err == ""
        assert home_dir.listdir() == []

    def test_main_verbose(
            self, monkeypatch, local_android_download_b64, home_dir, capfd):
        # in verbose mode, we tell at least what we do
        monkeypatch.setattr(sys, "argv", ["scriptname", "-v"])
        main()
        out, err = capfd.readouterr()
        assert out.startswith("the\nto\nof\n")
        assert err != ""
        assert "Path" not in err

    def test_main_verbose_increased(
            self, monkeypatch, local_android_download_b64, home_dir, capfd):
        # we can be more verbose
        # (also use --raw, because only this way we have debug output)
        monkeypatch.setattr(sys, "argv", ["scriptname", "-vv", "--raw"])
        main()
        out, err = capfd.readouterr()
        assert out == ""
        assert "Path" in err

    def test_main_existing_file_errors(
            self, monkeypatch, local_android_download_b64, home_dir, capfd):
        # we do not overwrite existing target files
        monkeypatch.setattr(sys, "argv", ["scriptname", "--outfile", "foo"])
        download_path = home_dir / "foo"
        download_path.write("foo")
        with pytest.raises(SystemExit):
            main()
        out, err = capfd.readouterr()
        assert "File exists" in err
        assert download_path.read() == "foo"  # original file unchanged

    def test_main_existing_file_errors_raw(
            self, monkeypatch, local_android_download_b64, home_dir, capfd):
        # we do not overwrite existing target files
        monkeypatch.setattr(sys, "argv", ["scriptname", "--raw"])
        download_path = home_dir / "en_wordlist.combined.gz"
        download_path.write("foo")
        with pytest.raises(SystemExit):
            main()
        out, err = capfd.readouterr()
        assert "File exists" in err
        assert download_path.read() == "foo"  # original file unchanged

    def test_main_outfile(
            self, monkeypatch, local_android_download_b64, home_dir):
        # we can give a path for outfile
        monkeypatch.setattr(sys, "argv", ["scriptname", "-o", "foo", ])
        download_path = home_dir / "foo"
        main()
        assert download_path.isfile()

    def test_main_lang(
            self, monkeypatch, local_android_download_b64, home_dir, capfd):
        # we can request a certain language
        monkeypatch.setattr(sys, "argv", ["scriptname", "-l", "de", ])
        main()
        out, err = capfd.readouterr()
        assert out == "der\nund\n"

    def test_main_offensive(
            self, monkeypatch, local_android_download_b64, home_dir, capfd):
        # we can request non-offensive lists
        monkeypatch.setattr(sys, "argv", ["scriptname", "--no-offensive", ])
        main()
        out, err = capfd.readouterr()
        assert "hardcore" not in out

    def test_main_lang_codes(self, monkeypatch, local_index, capfd):
        # we can ask for a list of available languages
        monkeypatch.setattr(
                sys, "argv", ["scriptname", "--lang-codes", "-v", ])
        with pytest.raises(SystemExit):
            main()
        out, err = capfd.readouterr()
        assert err == "The following language codes are available:\n"
        assert out.startswith("cs da de el")
