wordlist-gen
============

Create wordlists for `diceware`_ in a reproducable and easy manner.

This project provides tools for easy generation of wordlists that can
be used with `diceware`_ .


Install
--------

Clone repository from github::

  $ git clone https://github.com/ulif/wordlist-gen.git

Please consider using `virtualenv`_ for deployment.


Testing
-------

Tests require `py.test`_ being installed. In an activated `virtualenv`
it can be installed with `pip`_::

  (venv)$ pip install pytest

Afterwards, you can run tests like so::

  (venv)$ py.test

If you also install `tox`::

  (venv)$ pip install tox

then you can run all tests for all supported platforms at once::

  (venv)$ tox



.. _diceware: http://diceware.com/
.. _pip: https://pip.pypa.io/en/latest/
.. _py.test: https://pytest.org/
.. _virtualenv: https://virtualenv.pypa.io/
