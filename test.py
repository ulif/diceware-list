import sys
import pytest

from wordlist_gen import get_cmdline_args


@pytest.fixture
def dictfile(request, tmpdir):
    """py.test fixture providing a dictfile.

    The returned file is a py.local instance.
    """
    dictfile = tmpdir / "dictfile.txt"
    dictfile.write("foo\nbar\n")
    return dictfile


class TestArgParser(object):

    def test_sys_argv_as_fallback(self, monkeypatch, capfd):
        # if we deliver no args, `sys.argv` is used.
        monkeypatch.setattr(
            sys, "argv", ["scriptname", "rare_filename"])
        with pytest.raises(SystemExit):
            get_cmdline_args()
        out, err = capfd.readouterr()
        assert "rare_filename" in err

    def test_dict_file_required(self, monkeypatch, capfd):
        # we require at least one argument, a dictionary file
        monkeypatch.setattr(sys, "argv", ["scriptname", ])
        with pytest.raises(SystemExit) as why:
            get_cmdline_args()
        assert why.value.args[0] == 2
        out, err = capfd.readouterr()
        assert "the following arguments are required" in err

    def test_dict_file_must_exist(self, monkeypatch, capfd):
        # we require at least one argument, a dictionary file
        monkeypatch.setattr(sys, "argv", ["scriptname", "foobar"])
        with pytest.raises(SystemExit):
            get_cmdline_args()
        out, err = capfd.readouterr()
        assert "No such file or directory: 'foobar'" in err

    def test_opt_verbose_default(self, monkeypatch, capfd, tmpdir):
        # verbose option is unset by default.
        dictfile = tmpdir / "dictfile.txt"
        dictfile.write("foo")
        result = get_cmdline_args([str(dictfile), ])
        assert result.verbose is False

    def test_opt_verbose_settable(self, tmpdir):
        # we can set the verbose option
        dictfile = tmpdir / "dictfile.txt"
        dictfile.write("foo")
        result = get_cmdline_args(["-v", str(dictfile)])
        assert result.verbose is True
