import sys
import pytest
from io import StringIO
from wordlist_gen import get_cmdline_args, filtered_by_len


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
        if sys.version_info < (3,0):
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


def test_filtered_by_len():
    buf = StringIO(u"Line1\nLine12\n")
    result = list(filtered_by_len(buf))
    assert result == ["Line1", "Line12"]

def test_filtered_by_len_min_len():
    # we can set minimal length of accepted terms
    buf = StringIO(u"\n".join(["1", "12", "123", "1234"]))
    assert list(filtered_by_len(buf)) == ["123", "1234"]
    assert list(filtered_by_len(buf, min_len=2)) == ["12", "123", "1234"]
    assert list(filtered_by_len(buf, min_len=4)) == ["1234", ]
