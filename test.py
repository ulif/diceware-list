# -*- coding: utf-8 -*-
#  diceware_list -- generate wordlists for diceware
#  Copyright (C) 2016  Uli Fouquet
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
import os
import sys
import pytest
import random
from diceware_list import (
    DEFAULT_CHARS,
    get_cmdline_args, generate_wordlist, term_iterator, main, min_width_iter,
    base_terms_iterator, base10_to_n, idx_to_dicenums, filter_chars,
    shuffle_max_width_items, normalize
    )


@pytest.fixture
def dictfile(request, tmpdir):
    """py.test fixture providing a dictfile.

    The returned file is a py.local instance.
    """
    dictfile = tmpdir / "dictfile.txt"
    contents = "\n".join(["zzz%s" % x for x in range(8192)])
    dictfile.write("foo\nbar\n" + contents)
    return dictfile


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

    def test_options_defaults(self, dictfile):
        # options provide sensible defaults.
        result = get_cmdline_args([str(dictfile), ])
        assert result.verbose is None
        assert result.length == 8192
        assert result.numbered is False
        assert result.ascii_only is False
        assert result.sides == 6
        assert result.use_kit is True
        assert result.use_416 is False
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

    def test_opt_sides_settable(self, dictfile):
        # we can set the ``sides`` option
        result = get_cmdline_args(["-s 3", str(dictfile)])
        assert result.sides == 3
        result = get_cmdline_args(["--sides=10", str(dictfile)])
        assert result.sides == 10

    def test_opt_no_kit_settable(self, dictfile):
        # we can tell whether we want the diceware kit included
        result = get_cmdline_args(["-k", str(dictfile)])
        assert result.use_kit is False
        result = get_cmdline_args(["--no-kit", str(dictfile)])
        assert result.use_kit is False

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


class TestWordlistGen(object):
    # Minor components are grouped here

    def test_base10_to_n(self):
        # we can turn integers into n-based numbers
        assert base10_to_n(0, 2) == [0]
        assert base10_to_n(1, 2) == [1]
        assert base10_to_n(2, 2) == [1, 0]
        assert base10_to_n(3, 2) == [1, 1]
        assert base10_to_n(7775, 6) == [5, 5, 5, 5, 5]
        assert base10_to_n(0, 6) == [0, ]
        assert base10_to_n(1, 6) == [1, ]
        assert base10_to_n(6, 6) == [1, 0]
        assert base10_to_n(34, 6) == [5, 4]
        assert base10_to_n(35, 6) == [5, 5]
        assert base10_to_n(37, 6) == [1, 0, 1]
        assert base10_to_n(38, 6) == [1, 0, 2]

    def test_dicenums(self):
        # we can get dice numbers from list indexes
        assert idx_to_dicenums(0, 5) == "11111"
        assert idx_to_dicenums(1, 5) == "11112"
        assert idx_to_dicenums(7774, 5) == "66665"
        assert idx_to_dicenums(7775, 5) == "66666"
        # different dice sides, different results
        assert idx_to_dicenums(0, 4, 4) == "1111"
        assert idx_to_dicenums(255, 4, 4) == "4444"
        assert idx_to_dicenums(255, 4) == "2214"

    def test_term_iterator(self, tmpdir):
        # the term_iterator really returns iterators
        wlist = tmpdir.join("wlist.txt")
        wlist.write(b"\n".join([b"a", b"b", b"c"]))
        with open(str(wlist), "rb") as fd:
            result = list(term_iterator([fd, ]))
        assert result == [b"a", b"b", b"c"]

    def test_term_iterator_multiple_files(self, tmpdir):
        # we can feed multiple input files to term_iterator
        wlist1 = tmpdir.join("wlist1.txt")
        wlist2 = tmpdir.join("wlist2.txt")
        wlist1.write(b"\n".join([b"a1", b"b1", b"c1"]))
        wlist2.write(b"\n".join([b"a2", b"b2", b"c2"]))
        with open(str(wlist1), "rb") as fd1:
            with open(str(wlist2), "rb") as fd2:
                result = list(term_iterator([fd1, fd2]))
        assert result == [b"a1", b"b1", b"c1", b"a2", b"b2", b"c2"]

    def test_term_iterator_handles_umlauts(self, tmpdir):
        # we can feed term iterators with umlauts
        wlist = tmpdir.join("wlist.txt")
        wlist.write_text(u"ä\nö\n", "utf-8")
        with open(str(wlist), "r") as fd:
            result = list(term_iterator([fd, ]))
        assert result == ["ä", "ö"]

    def test_term_iterator_ignores_empty_lines(self, tmpdir):
        # empty lines will be ignored
        wlist = tmpdir.join("wlist.txt")
        wlist.write("foo\n\nbar\n\n")
        with open(str(wlist), "r") as fd:
            result = list(term_iterator([fd, ]))
        assert result == ["foo", "bar"]

    def test_min_width_iter(self, monkeypatch):
        # we can get iterators with minimal list width.
        monkeypatch.setattr(random, "shuffle", lambda x: x)
        assert list(min_width_iter(["bb", "a", "ccc", "dd"], 3)) == [
            "a", "bb", "dd"]
        assert list(min_width_iter(["c", "a", "b"], 2)) == ["a", "b"]
        assert list(min_width_iter(["c", "a", "b"], 3)) == ["a", "b", "c"]
        assert list(min_width_iter(["a", "c", "bb"], 2)) == ["a", "c"]
        assert list(min_width_iter(["a", "cc", "b"], 2)) == ["a", "b"]
        assert list(min_width_iter(["aa", "c", "bb"], 2)) == ["c", "aa"]

    def test_min_width_iter_shuffle_max_widths_values(self, monkeypatch):
        # words with maximum width are shuffled
        monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
        assert list(min_width_iter(
            ["a", "aa", "bb"], 2, shuffle_max_width=True)) == ["a", "bb"]

    def test_min_width_iter_shuffling_ignores_too_longs(self, monkeypatch):
        # we determine the max_width correctly
        monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
        assert list(min_width_iter(
            ["bbb", "aa", "a"], 2, shuffle_max_width=True)) == ["a", "aa"]
        assert list(min_width_iter(
            ["aa", "a"], 2, shuffle_max_width=True)) == ["a", "aa"]

    def test_main_script_runnable(self, capfd):
        # we can run the main script as simple python script.
        script_loc = os.path.join(
            os.path.dirname(__file__), 'diceware_list.py')
        python_exe = sys.executable
        status = os.system("%s %s --help" % (python_exe, script_loc))
        out, err = capfd.readouterr()
        assert out.startswith("usage: diceware_list.py")
        assert status == 0

    def test_base_terms_iterator(self):
        # we can get an iterator over base terms
        base_iter = base_terms_iterator()
        base_list = list(base_iter)
        assert "a2" in base_list
        assert "9z" in base_list
        assert "0" in base_list
        assert "zzzz" in base_list

    def test_base_terms_iterator_option_use_kit(self):
        # we can tell whether to use dicewarekit, diceware416 lists.
        assert "yyyy" not in list(base_terms_iterator(use_kit=False))
        assert "a2" in list(base_terms_iterator(use_kit=False))
        assert "yyyy" in list(base_terms_iterator(use_kit=True))
        assert "a2" in list(base_terms_iterator(use_kit=True))

    def test_filter_chars(self):
        # we can detect words with unwanted chars
        assert list(filter_chars([], DEFAULT_CHARS)) == []
        assert list(filter_chars(["a", "b"], DEFAULT_CHARS)) == ["a", "b"]
        assert list(filter_chars(["ä"], DEFAULT_CHARS)) == []
        assert list(filter_chars(["a", "ä"], DEFAULT_CHARS)) == ["a"]
        assert list(filter_chars(["ä", "a"], DEFAULT_CHARS)) == ["a"]
        assert list(filter_chars(["a", "ä", "b"], DEFAULT_CHARS)) == ["a", "b"]
        assert list(filter_chars(["a", "aä", "bö"], DEFAULT_CHARS)) == ["a"]
        assert list(filter_chars([u"a", u"ä"], DEFAULT_CHARS)) == [u"a"]

    def test_filter_chars_all_allowed(self):
        # if `allowed` is None, no filtering will be done
        assert list(filter_chars(['ä'], None)) == ['ä']

    def test_shuffle_max_width_items(self, monkeypatch):
        # we can shuffle the max width items of a list
        # install a pseudo-shuffler that generates predictable orders
        monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
        in_list = ["a", "aa", "bb", "cc"]
        result = list(shuffle_max_width_items(in_list))
        # last elements are returned in reverse order.
        assert result == ["a", "cc", "bb", "aa"]

    def test_shuffle_max_width_items_unsorted_input(self, monkeypatch):
        # we can shuffle the max width items of an unsorted list
        # install a pseudo-shuffler that generates predictable orders
        monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
        in_list = ["aa", "d", "bb", "a", "cc"]
        result = list(shuffle_max_width_items(in_list))
        # last elements are returned in reverse order.
        assert result == ["d", "a", "cc", "bb", "aa"]

    def test_shuffle_max_width_items_drop_over_max_width(self, monkeypatch):
        # with a given max_width we drop words that are longer
        monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
        in_list = ["eeee", "bb", "ccc", "aa", "ddd"]
        result = list(shuffle_max_width_items(in_list, max_width=3))
        assert "eeee" not in result

    def test_normalize(self):
        assert normalize(u"ªºÀÁÂÃÄÅÆ") == "aoAAAAAEAAE"
        assert normalize(u"ÇÈÉÊËÌÍÎÏ") == "CEEEEIIII"
        assert normalize(u"ÒÓÔÕÖØÙÚÛÜ") == "OOOOOEOEUUUUE"
        # "ÐÑÝßàáâãäåæçèéêëìíîïñòóôõöøùúûüý"
        # "þÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİ"
        # "ıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖŗŘřŚśŜŝŞşŠšŢţ"
        # "ŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽžſƀƁƂƃƄƅƆƇƈƉƊƋƌƍ"
        assert normalize(u"mäßig") == u"maessig"


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
        assert "!" in result_default

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
        assert sides_2_list == ['111 a', '112 b', '121 c', '122 d', '211 e']
        assert sides_3_list == ['11 a', '12 b', '13 c', '21 d', '22 e', '23 f']
        assert default_list == [
            '11 a', '12 b', '13 c', '14 d', '15 e', '16 f', '21 g']

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

    def test_main_output(self, monkeypatch, capfd, dictfile):
        # we can output simple lists
        monkeypatch.setattr(sys, "argv", ["scriptname", str(dictfile)])
        main()
        out, err = capfd.readouterr()
        assert "\nbar\n" in out
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
        # we do not include the diceware kit if told so.
        monkeypatch.setattr(
            sys, "argv", ["scriptname", str(dictfile)])  # no '-k'
        main()
        out, err = capfd.readouterr()
        assert "!" in out
        monkeypatch.setattr(
            sys, "argv", ["scriptname", "-k", str(dictfile)])
        main()
        out, err = capfd.readouterr()
        assert "!" not in out

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
            sys, "argv", ["scriptname", "-l", "3", "-k", str(dictfile)])
        main()
        out, err = capfd.readouterr()
        assert out == u"aa\naä\nba\n"
        monkeypatch.setattr(
            sys, "argv",
            ["scriptname", "-l", "2", "-k", "--ascii", str(dictfile)])
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

    def test_main_sides(self, monkeypatch, dictfile, capfd):
        # we support unusual dice
        alphabet = "".join(
            [u"%s\n" % x for x in u"ABCDEDFGHIJKLMNOPQRSTUVWXYZ"])
        dictfile.write_text(alphabet, "utf-8")
        monkeypatch.setattr(
            sys, "argv", [   # no "-s"
                "scriptname", "-n", "-l", "26", "-k", str(dictfile)
                ])
        main()
        out, err = capfd.readouterr()
        assert "52 z" in out
        assert "211 z" not in out
        monkeypatch.setattr(
            sys, "argv", [
                "scriptname", "-n", "-s", "5", "-l", "26", "-k", str(dictfile)
                ])
        main()
        out, err = capfd.readouterr()
        assert "52 z" not in out
        assert "211 z" in out
