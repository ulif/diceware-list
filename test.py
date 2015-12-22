import sys
import pytest

from wordlist_gen import get_cmdline_args


class TestArgParser(object):

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
