# -*- coding: utf-8 -*-
#  diceware_list -- generate wordlists for diceware
#  Copyright (C) 2016-2017  Uli Fouquet
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
"""diceware_list -- wordlists for diceware.
"""
import sys
import pytest
import random
from diceware_list import (
        get_cmdline_args, generate_wordlist, main, __version__
        )


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


class TestHelpers(object):

    def test_version(self):
        assert __version__ is not None


class TestArgParser(object):

    def test_sys_argv_as_fallback(self, monkeypatch, capfd, dictfile):
        # if we deliver no args, `sys.argv` is used.
        monkeypatch.setattr(sys, "argv", ["scriptname", str(dictfile)])
        get_cmdline_args()
        out, err = capfd.readouterr()
        assert err == ""

    def test_dict_file_required(self, capfd):
        # we require at least one argument, a dictionary file
        with pytest.raises(SystemExit) as why:
            get_cmdline_args(None)
        assert why.value.args[0] == 2
        out, err = capfd.readouterr()
        if sys.version_info < (3, 0):
            assert "too few arguments" in err
        else:
            assert "the following arguments are required" in err

    def test_dict_file_must_exist(self, monkeypatch, capfd):
        # we require at least one argument, a dictionary file
        with pytest.raises(SystemExit):
            get_cmdline_args(["foobar", ])
        out, err = capfd.readouterr()
        assert "No such file or directory: 'foobar'" in err

    def test_version(self, monkeypatch, capfd):
        # we can output current version.
        with pytest.raises(SystemExit):
            get_cmdline_args(["--version", ])
        out, err = capfd.readouterr()
        assert __version__ in (out + err)

    def test_prefix_options_req_certain_keywords(self, monkeypatch, capfd):
        # we require one of 'short', 'long', 'short' as ``--prefix``.
        with pytest.raises(SystemExit):
            get_cmdline_args(["--prefix", "invalid-keyword", ])
        out, err = capfd.readouterr()
        assert "--prefix: invalid choice" in (out + err)

    def test_options_defaults(self, dictfile):
        # options provide sensible defaults.
        result = get_cmdline_args([str(dictfile), ])
        assert result.verbose is None
        assert result.length == 8192
        assert result.numbered is False
        assert result.ascii_only is False
        assert result.sides == 6
        assert result.use_kit is False
        assert result.use_416 is False
        assert result.prefix == 'none'
        assert isinstance(result.dictfile, list)

    def test_arg_dictfile_gives_file_objs(self, tmpdir):
        path1 = tmpdir / "foo.txt"
        path2 = tmpdir / "bar.txt"
        path1.write("foo")
        path2.write("bar")
        result = get_cmdline_args([str(path1), str(path2)])
        assert len(result.dictfile) == 2
        assert result.dictfile[0].read() == "foo"
        assert result.dictfile[1].read() == "bar"

    def test_opt_verbose_settable(self, dictfile):
        # we can set the verbose option
        result = get_cmdline_args(["-v", str(dictfile)])
        assert result.verbose == 1
        result = get_cmdline_args(["-vvv", str(dictfile)])
        assert result.verbose == 3

    def test_opt_length_settable(self, dictfile):
        # we can set the length option
        result = get_cmdline_args(["-l 1024", str(dictfile)])
        assert result.length == 1024
        result = get_cmdline_args(["--length=2048", str(dictfile)])
        assert result.length == 2048

    def test_opt_ascii_settable(self, dictfile):
        # we can set the ascii_only option
        result = get_cmdline_args(["--ascii", str(dictfile)])
        assert result.ascii_only is True

    def test_opt_dice_sides_settable(self, dictfile):
        # we can set the ``dice-sides`` option
        result = get_cmdline_args(["-d 3", str(dictfile)])
        assert result.sides == 3
        result = get_cmdline_args(["--sides=10", str(dictfile)])
        assert result.sides == 10

    def test_opt_no_kit_settable(self, dictfile):
        # we can tell whether we want the diceware kit included
        result = get_cmdline_args(["-k", str(dictfile)])
        assert result.use_kit is True
        result = get_cmdline_args(["--use-kit", str(dictfile)])
        assert result.use_kit is True

    def test_opt_use_416_settable(self, dictfile):
        # we can tell to use the diceware416.txt list.
        result = get_cmdline_args(["--use-416", str(dictfile)])
        assert result.use_416 is True

    def test_opt_numbered_settable(self, dictfile):
        # we can tell if we want numbers in output.
        result = get_cmdline_args(["-n", str(dictfile)])
        assert result.numbered is True
        result = get_cmdline_args(["--numbered", str(dictfile)])
        assert result.numbered is True

    def test_opt_prefix_settable(self, dictfile):
        # we can tell whether we want prefix code (and which one)
        result = get_cmdline_args(["-p", "none", str(dictfile)])
        assert result.prefix == 'none'
        result = get_cmdline_args(["--prefix", "none", str(dictfile)])
        assert result.prefix == 'none'
        result = get_cmdline_args(["-p", "short", str(dictfile)])
        assert result.prefix == 'short'
        result = get_cmdline_args(["--prefix", "short", str(dictfile)])
        assert result.prefix == 'short'
        result = get_cmdline_args(["-p", "long", str(dictfile)])
        assert result.prefix == 'long'
        result = get_cmdline_args(["--prefix", "long", str(dictfile)])
        assert result.prefix == 'long'


class TestGenerateWordlist(object):

    def test_arg_length_is_respected(self, monkeypatch):
        # we respect the "length" parameter
        monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
        in_list = ["a", "b", "c"]
        assert list(generate_wordlist(in_list, length=0)) == []
        assert list(
            generate_wordlist(
                in_list, length=1, use_kit=False)) == ["c", ]
        assert list(
            generate_wordlist(
                in_list, length=2, use_kit=False)) == ["b", "c"]
        assert list(
            generate_wordlist(
                in_list, length=3, use_kit=False)) == ["a", "b", "c"]
        with pytest.raises(ValueError):
            list(generate_wordlist(in_list, length=4, use_kit=False))

    def test_arg_lowercase_is_respected(self):
        # we respect the "lowercase" parameter
        in_list = ["a", "B", "C"]
        mixed = list(
            generate_wordlist(
                in_list, length=3, lowercase=False, use_kit=False))
        lower = list(
            generate_wordlist(
                in_list, length=3, lowercase=True, use_kit=False))
        default = list(generate_wordlist(in_list, length=3, use_kit=False))
        assert "a" in mixed
        assert "B" in mixed
        assert "a" in lower
        assert "b" in lower
        assert "a" in default
        assert "b" in default

    def test_arg_use_kit_is_respected(self, monkeypatch):
        # we respect the "use_kit" parameter
        monkeypatch.setattr(random, "shuffle", lambda x: x)
        result1 = list(generate_wordlist(["a", "b"], length=3, use_kit=True))
        result2 = list(generate_wordlist(["a", "b"], length=2, use_kit=False))
        result_default = list(generate_wordlist(["a", "b"], length=2))
        assert "!" in result1
        assert "!" not in result2
        assert "!" not in result_default

    def test_arg_use_416_is_respected(self, monkeypatch):
        # we respect the "use_416" parameter
        monkeypatch.setattr(random, "shuffle", lambda x: x)
        result1 = list(
            generate_wordlist(
                ["a", "b"], length=3, use_kit=False, use_416=True))
        result2 = list(
            generate_wordlist(
                ["a", "b"], length=2, use_kit=False, use_416=False))
        result_default = list(
            generate_wordlist(["a", "b"], length=2, use_kit=False))
        assert "2a" in result1
        assert "2a" not in result2
        assert "2a" not in result_default

    def test_arg_numbered_is_respected(self):
        # we consider the 'numbered' parameter
        terms = ["term%s" % x for x in range(7776)]
        no_num_list = list(generate_wordlist(
            terms, length=7776, use_kit=False, use_416=False, numbered=False))
        numbered_list = list(generate_wordlist(
            terms, length=7776, use_kit=False, use_416=False, numbered=True))
        default_list = list(generate_wordlist(
            terms, length=7776, use_kit=False, use_416=False))
        assert len(no_num_list[0].split()) == 1
        assert len(numbered_list[0].split()) == 2
        assert len(default_list[0].split()) == 1

    def test_arg_ascii_only_is_respected(self, monkeypatch):
        # we respect ascii_only.
        monkeypatch.setattr(random, "shuffle", lambda x: x)
        terms = [u"aa", u"aä", u"ba"]
        unfiltered_list = list(generate_wordlist(
            terms, length=2, use_kit=False, use_416=False, ascii_only=False))
        filtered_list = list(generate_wordlist(
            terms, length=2, use_kit=False, use_416=False, ascii_only=True))
        default_list = list(generate_wordlist(
            terms, length=2, use_kit=False, use_416=False))
        assert unfiltered_list == [u"aa", u"aä"]
        assert filtered_list == [u"aa", u"ba"]
        assert default_list == unfiltered_list

    def test_arg_shuffle_max_is_respected(self, monkeypatch):
        # we can switch shuffling on or off.
        monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
        terms = ['a', 'b', 'c']
        unshuffled_list = list(generate_wordlist(
            terms, length=2, use_kit=False, use_416=False, shuffle_max=False))
        shuffled_list = list(generate_wordlist(
            terms, length=2, use_kit=False, use_416=False, shuffle_max=True))
        default_list = list(generate_wordlist(
            terms, length=2, use_kit=False, use_416=False))
        assert unshuffled_list == [u'a', u'b']
        assert shuffled_list == [u'b', u'c']
        assert default_list == shuffled_list

    def test_arg_sides_is_respected(self, monkeypatch):
        # we can choose how much sides the used dice have
        monkeypatch.setattr(random, "shuffle", lambda x: x)
        terms = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        sides_2_list = list(generate_wordlist(
            terms, length=5, use_kit=False, use_416=False, numbered=True,
            dice_sides=2))
        sides_3_list = list(generate_wordlist(
            terms, length=6, use_kit=False, use_416=False, numbered=True,
            dice_sides=3))
        default_list = list(generate_wordlist(
            terms, length=7, use_kit=False, use_416=False, numbered=True))
        assert sides_2_list == [
            '111 a', '112 b', '121 c', '122 d', '211 e']
        assert sides_3_list == [
            '11 a', '12 b', '13 c', '21 d', '22 e', '23 f']
        assert default_list == [
            '11 a', '12 b', '13 c', '14 d', '15 e', '16 f', '21 g']

    def test_arg_delimiter_default(self, monkeypatch):
        # we can choose how numbered output separates numbers.
        monkeypatch.setattr(random, "shuffle", lambda x: x)
        terms = ['w%s' % x for x in range(7)]  # ['w0'..'w6']
        default_list = list(generate_wordlist(
            terms, length=7, use_kit=False, use_416=False, numbered=True))
        assert default_list == [
            '11 w0', '12 w1', '13 w2', '14 w3', '15 w4', '16 w5', '21 w6']

    def test_arg_delimiter_more_than_9_sides(self, monkeypatch):
        # with more than 9 sides, we output dashes in numbered output
        monkeypatch.setattr(random, "shuffle", lambda x: x)
        terms = ['w%02d' % x for x in range(11)]  # ['w00'..'w10']
        d10_list = list(generate_wordlist(
            terms, length=11, use_kit=False, use_416=False,
            numbered=True, dice_sides=10))
        assert d10_list == [
            '1-1 w00', '1-2 w01', '1-3 w02', '1-4 w03', '1-5 w04', '1-6 w05',
            '1-7 w06', '1-8 w07', '1-9 w08', '1-10 w09', '2-1 w10']

    def test_arg_prefix_code_is_respected(self, monkeypatch):
        # we can tell whether prefix code should be generated
        monkeypatch.setattr(random, "shuffle", lambda x: x)
        terms = ['a', 'aa', 'ba', 'ca']
        result1 = list(generate_wordlist(
            terms, length=3, use_kit=False, use_416=False,
            prefix_code='none'))
        result2 = list(generate_wordlist(
            terms, length=3, use_kit=False, use_416=False,
            prefix_code='short'))
        result3 = list(generate_wordlist(
            terms, length=3, use_kit=False, use_416=False,
            prefix_code='long'))
        assert result1 == ['a', 'aa', 'ba']
        assert result2 == ['a', 'ba', 'ca']
        assert result3 == ['aa', 'ba', 'ca']

    def test_result_sorted(self):
        # result iterators are sorted
        in_list = ["c", "aa", "a", "b"]
        assert list(
            generate_wordlist(in_list, length=4, use_kit=False)
            ) == ["a", "aa", "b", "c"]

    def test_unique_entries_only(self):
        # wordlists contain each entry only once
        in_list = ["a", "a", "a", "b", "a"]
        assert list(
            generate_wordlist(in_list, length=2, use_kit=False)
            ) == ["a", "b"]

    def test_wordlist_too_short(self):
        # wordlists that are too short raise a special exception
        in_list = ["1", "2", "3"]
        with pytest.raises(ValueError):
            list(generate_wordlist(in_list, length=4, use_kit=False))


class TestMain(object):

    def test_main(self, monkeypatch):
        # we can call the main function (although it will require extra args)
        monkeypatch.setattr(sys, "argv", ["scriptname", ])
        with pytest.raises(SystemExit):
            main()

    def test_main_help(self, monkeypatch, capfd):
        # we can get --help
        monkeypatch.setattr(sys, "argv", ["scriptname", "--help"])
        with pytest.raises(SystemExit):
            main()
        out, err = capfd.readouterr()
        assert "positional arguments" in out

    def test_main_version(self, monkeypatch, capfd):
        # we can get --version
        monkeypatch.setattr(sys, "argv", ["scriptname", "--version"])
        with pytest.raises(SystemExit):
            main()
        out, err = capfd.readouterr()
        assert __version__ in out + err

    def test_main_output(self, monkeypatch, capfd, dictfile):
        # we can output simple lists
        monkeypatch.setattr(sys, "argv", ["scriptname", str(dictfile)])
        main()
        out, err = capfd.readouterr()
        assert "\nfoo\n" in out

    def test_main_length(self, monkeypatch, tmpdir, capfd):
        # we do not output more terms than requested.
        wlist_path = tmpdir / "wlist.txt"
        wlist_path.write("1\n2\n3\n")
        monkeypatch.setattr(
            sys, "argv", ["scriptname", "-l", "2", str(wlist_path)])
        main()
        out, err = capfd.readouterr()
        assert out.count("\n") == 2

    def test_main_no_kit(self, monkeypatch, dictfile, capfd):
        # we do not include the diceware kit by default.
        monkeypatch.setattr(
            sys, "argv", ["scriptname", str(dictfile)])  # no '-k'
        main()
        out, err = capfd.readouterr()
        assert "!" not in out
        monkeypatch.setattr(
            sys, "argv", ["scriptname", "-k", str(dictfile)])
        main()
        out, err = capfd.readouterr()
        assert "!" in out

    def test_main_use_416(self, monkeypatch, dictfile, capfd):
        # we include the dieceware416.txt list if told.
        monkeypatch.setattr(
            sys, "argv", ["scriptname", str(dictfile)])  # no '--use-416'
        main()
        out, err = capfd.readouterr()
        assert "9z" not in out
        monkeypatch.setattr(
            sys, "argv", ["scriptname", "--use-416", str(dictfile)])
        main()
        out, err = capfd.readouterr()
        assert "9z" in out

    def test_main_numbered(self, monkeypatch, dictfile, capfd):
        # we can get dice numbers in output
        monkeypatch.setattr(
            sys, "argv", ["scriptname", "-n", "-l", "7776", str(dictfile)])
        main()
        out, err = capfd.readouterr()
        assert out.startswith("11111 ")

    def test_main_ascii_only(self, monkeypatch, dictfile, capfd):
        # we can tell to discard non-ASCII chars
        dictfile.write_text(u"aa\naä\nba\n", "utf-8")
        monkeypatch.setattr(
            sys, "argv", ["scriptname", "-l", "3", str(dictfile)])
        main()
        out, err = capfd.readouterr()
        assert out == u"aa\naä\nba\n"
        monkeypatch.setattr(
            sys, "argv",
            ["scriptname", "-l", "2", "--ascii", str(dictfile)])
        main()
        out, err = capfd.readouterr()
        assert out == u"aa\nba\n"

    def test_main_verbose(self, monkeypatch, dictfile, capfd):
        # we can require verbose output
        monkeypatch.setattr(sys, "argv", ["scriptname", "-v", str(dictfile)])
        main()
        out, err = capfd.readouterr()
        assert "Creating wordlist" in err
        assert "Verbose logging" not in err

    def test_main_verbose_verbose(self, monkeypatch, dictfile, capfd):
        # we can require very verbose output
        monkeypatch.setattr(sys, "argv", ["scriptname", "-vv", str(dictfile)])
        main()
        out, err = capfd.readouterr()
        assert "Creating wordlist" in err
        assert "Verbose logging" in err

    def test_main_prefix_unset(self, monkeypatch, dictfile_ext, capfd):
        # unset `prefix` option means no prefix filtering at all
        monkeypatch.setattr(sys, "argv", ["scriptname", str(dictfile_ext)])
        main()
        out, err = capfd.readouterr()
        assert "bb\nbbb\n" in out

    def test_main_prefix_none(self, monkeypatch, dictfile_ext, capfd):
        # we can turn off prefix filtering
        monkeypatch.setattr(sys, "argv", [
            "scriptname", "--prefix=none", str(dictfile_ext)])
        main()
        out, err = capfd.readouterr()
        assert "bb\nbbb\n" in out

    def test_main_prefix_short(self, monkeypatch, dictfile_ext, capfd):
        # we can ask for prefix filtering with short prefixes kept
        monkeypatch.setattr(sys, "argv", [
            "scriptname", "--prefix=short", str(dictfile_ext)])
        main()
        out, err = capfd.readouterr()
        assert "a\nbb\nc" in out
        assert "bbb" not in out

    def test_main_prefix_long(self, monkeypatch, dictfile_ext, capfd):
        # we can ask for prefix filtering with long prefixes kept
        monkeypatch.setattr(sys, "argv", [
            "scriptname", "--prefix=long", str(dictfile_ext)])
        main()
        out, err = capfd.readouterr()
        assert "a\nbb\nc" not in out
        assert "bbb" in out

    def test_main_sides(self, monkeypatch, dictfile, capfd):
        # we support unusual dice
        alphabet = "".join(
            [u"%s\n" % x for x in u"ABCDEDFGHIJKLMNOPQRSTUVWXYZ"])
        dictfile.write_text(alphabet, "utf-8")
        monkeypatch.setattr(
            sys, "argv", [   # no "-d"
                "scriptname", "-n", "-l", "26", str(dictfile)
                ])
        main()
        out, err = capfd.readouterr()
        assert "52 z" in out
        assert "211 z" not in out
        monkeypatch.setattr(
            sys, "argv", [
                "scriptname", "-n", "-l", "26", "-d", "5", str(dictfile)
                ])
        main()
        out, err = capfd.readouterr()
        assert "52 z" not in out
        assert "211 z" in out
