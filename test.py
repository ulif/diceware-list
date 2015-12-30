import sys
import pytest
from io import StringIO
from wordlist_gen import (
    get_cmdline_args, filtered_by_len, generate_wordlist, term_iterator, main
    )


@pytest.fixture
def dictfile(request, tmpdir):
    """py.test fixture providing a dictfile.

    The returned file is a py.local instance.
    """
    dictfile = tmpdir / "dictfile.txt"
    dictfile.write("foo\nbar\n")
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
        assert result.len == 8192
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

    def test_opt_len_settable(self, dictfile):
        # we can set the len option
        result = get_cmdline_args(["-l 1024", str(dictfile)])
        assert result.len == 1024


class TestFilteredByLen(object):

    def test_filtered_by_len(self):
        buf = StringIO(u"Line1\nLine12\n")
        result = list(filtered_by_len(buf))
        assert result == ["Line1", "Line12"]

    def test_filtered_by_len_min_len(self):
        # we can set minimal length of accepted terms
        buf = StringIO(u"\n".join(["1", "12", "123", "1234"]))
        assert list(filtered_by_len(buf)) == ["123", "1234"]
        assert list(filtered_by_len(buf, min_len=2)) == ["12", "123", "1234"]
        assert list(filtered_by_len(buf, min_len=4)) == ["1234", ]

    def test_filtered_by_len_max_len(self):
        #  we can set maximum length of accepted terms
        buf = StringIO(u"\n".join(["123", "1234", "12345"]))
        assert list(filtered_by_len(buf)) == ["123", "1234", "12345"]
        assert list(filtered_by_len(buf, max_len=3)) == ["123", ]
        assert list(filtered_by_len(buf, max_len=4)) == ["123", "1234"]


class TestTermIterator(object):

    def test_term_iterator(self, tmpdir):
        wlist = tmpdir.join("wlist.txt")
        wlist.write(b"\n".join([b"a", b"b", b"c"]))
        with open(str(wlist), "rb") as fd:
            result = list(term_iterator([fd, ]))
        assert result == ["a", "b", "c"]

    def test_term_iterator_multiple_files(self, tmpdir):
        wlist1 = tmpdir.join("wlist1.txt")
        wlist2 = tmpdir.join("wlist2.txt")
        wlist1.write(b"\n".join([b"a1", b"b1", b"c1"]))
        wlist2.write(b"\n".join([b"a2", b"b2", b"c2"]))
        with open(str(wlist1), "rb") as fd1:
            with open(str(wlist2), "rb") as fd2:
                result = list(term_iterator([fd1, fd2]))
        assert result == ["a1", "b1", "c1", "a2", "b2", "c2"]


class TestGenerateWordlist(object):

    def test_arg_length_is_respected(self):
        # we respect the "length" parameter
        in_list = ["a", "b", "c"]
        assert list(generate_wordlist(in_list, length=0)) == []
        assert list(generate_wordlist(in_list, length=1)) == ["a", ]
        assert list(generate_wordlist(in_list, length=2)) == ["a", "b"]
        assert list(generate_wordlist(in_list, length=3)) == ["a", "b", "c"]
        assert list(generate_wordlist(in_list, length=4)) == ["a", "b", "c"]


class TestMain(object):

    def test_main(self, monkeypatch):
        # we can call the main function (although it will require extra args)
        monkeypatch.setattr(sys, "argv", ["scriptname", ])
        with pytest.raises(SystemExit):
            main()
