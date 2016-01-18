# -*- coding: utf-8 -*-
import os
import sys
import pytest
from wordlist_gen import (
    get_cmdline_args, filtered_by_len, generate_wordlist, term_iterator, main,
    min_width_iter, base_terms_iterator
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
        assert result.verbose is False
        assert result.length == 8192
        assert isinstance(result.dictfile, list)

    def test_arg_dictfile_gives_file_objs(self, tmpdir):
        path1 = tmpdir / "foo.txt"
        path2 = tmpdir / "bar.txt"
        path1.write("foo")
        path2.write("bar")
        result = get_cmdline_args([str(path1), str(path2)])
        assert len(result.dictfile) == 2
        assert result.dictfile[0].read() == b"foo"
        assert result.dictfile[1].read() == b"bar"

    def test_opt_verbose_settable(self, dictfile):
        # we can set the verbose option
        result = get_cmdline_args(["-v", str(dictfile)])
        assert result.verbose is True

    def test_opt_length_settable(self, dictfile):
        # we can set the length option
        result = get_cmdline_args(["-l 1024", str(dictfile)])
        assert result.length == 1024
        result = get_cmdline_args(["--length=2048", str(dictfile)])
        assert result.length == 2048


class TestWordlistGen(object):
    # Minor components are grouped here

    def test_filtered_by_len(self):
        terms = ["Line1", "Line12"]
        result = list(filtered_by_len(terms))
        assert result == ["Line1", "Line12"]

    def test_filtered_by_len_min_len(self):
        # we can set minimal length of accepted terms
        terms = ["1", "12", "123", "1234"]
        assert list(filtered_by_len(terms)) == ["123", "1234"]
        assert list(filtered_by_len(terms, min_len=2)) == ["12", "123", "1234"]
        assert list(filtered_by_len(terms, min_len=4)) == ["1234", ]

    def test_filtered_by_len_max_len(self):
        #  we can set maximum length of accepted terms
        terms = ["123", "1234", "12345"]
        assert list(filtered_by_len(terms)) == ["123", "1234", "12345"]
        assert list(filtered_by_len(terms, max_len=3)) == ["123", ]
        assert list(filtered_by_len(terms, max_len=4)) == ["123", "1234"]

    def test_filtered_by_len_handle_umlauts(self):
        # we can handle umlauts
        terms = [u"törm", u"ümläut"]
        assert list(filtered_by_len(terms)) == [u"törm", u"ümläut"]

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

    def test_min_width_iter(self):
        # we can get iterators with minimal list width.
        assert list(min_width_iter(["bb", "a", "ccc", "dd"], 3)) == [
            "a", "bb", "dd"]
        assert list(min_width_iter(["c", "a", "b"], 2)) == ["a", "b"]
        assert list(min_width_iter(["c", "a", "b"], 3)) == ["a", "b", "c"]
        assert list(min_width_iter(["a", "c", "bb"], 2)) == ["a", "c"]
        assert list(min_width_iter(["a", "cc", "b"], 2)) == ["a", "b"]
        assert list(min_width_iter(["aa", "c", "bb"], 2)) == ["c", "aa"]

    def test_main_script_runnable(self, capfd):
        # we can run the main script as simple python script.
        script_loc = os.path.join(
            os.path.dirname(__file__), 'wordlist_gen.py')
        python_exe = sys.executable
        status = os.system("%s %s --help" % (python_exe, script_loc))
        out, err = capfd.readouterr()
        assert out.startswith("usage: wordlist_gen.py")
        assert status == 0

    def test_base_terms_iterator(self):
        # we can get an iterator over base terms
        base_iter = base_terms_iterator()
        base_list = list(base_iter)
        assert b"a2" in base_list
        assert b"9z" in base_list
        assert b"0" in base_list
        assert b"zzzz" in base_list


class TestGenerateWordlist(object):

    def test_arg_length_is_respected(self):
        # we respect the "length" parameter
        in_list = ["a", "b", "c"]
        assert list(generate_wordlist(in_list, length=0)) == []
        assert list(generate_wordlist(in_list, length=1)) == ["a", ]
        assert list(generate_wordlist(in_list, length=2)) == ["a", "b"]
        assert list(generate_wordlist(in_list, length=3)) == ["a", "b", "c"]
        with pytest.raises(ValueError):
            list(generate_wordlist(in_list, length=4))

    def test_result_sorted(self):
        # result iterators are sorted
        in_list = ["c", "aa", "a", "b"]
        assert list(
            generate_wordlist(in_list, length=4)) == ["a", "aa", "b", "c"]

    def test_unique_entries_only(self):
        # wordlists contain each entry only once
        in_list = ["a", "a", "a", "b", "a"]
        assert list(generate_wordlist(in_list, length=2)) == ["a", "b"]

    def test_wordlist_too_short(self):
        # wordlists that are too short raise a special exception
        in_list = ["1", "2", "3"]
        with pytest.raises(ValueError):
            list(generate_wordlist(in_list, length=4))


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
        assert out.startswith("bar\nfoo\n")

    def test_main_length(self, monkeypatch, tmpdir, capfd):
        # we do not output more terms than requested.
        wlist_path = tmpdir / "wlist.txt"
        wlist_path.write("1\n2\n3\n")
        monkeypatch.setattr(
            sys, "argv", ["scriptname", "-l", "2", str(wlist_path)])
        main()
        out, err = capfd.readouterr()
        assert out == "1\n2\n"
