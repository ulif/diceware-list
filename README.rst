diceware-list
=============

|bdg-build| `sources <https://github.com/ulif/diceware-list>`_ | `issues <https://github.com/ulif/diceare-list/issues>`_

.. |bdg-build| image:: https://travis-ci.org/ulif/diceare-list.svg?branch=master
    :target: https://travis-ci.org/ulif/diceare-list
    :alt: Build Status

Create wordlists for `diceware`_ in a reproducable and easy manner.

This is not a `diceware`_ implementationm, but only a helper to create
appropriate wordlists.


Install
--------

Clone repository from github::

  $ git clone https://github.com/ulif/diceare-list.git

Please consider using `virtualenv`_ for deployment.

In an active virtualenv you can install an executable script of
`diceare-list` running::

  (venv) $ python setup.py install
  (venv) $ diceware_list --help
  usage: diceware_list [-h] [-l LENGTH] [-k] [--use-416] [-v] DICTFILE

But you can also run the one and only script directly::

  $ python diceware_list.py --help
  usage: diceware_list [-h] [-l LENGTH] [-k] [--use-416] [-v] DICTFILE


Usage
-----

First, you need a file with words as "dictionary". On typical Debian
systems such files can be found in ``/usr/share/dicts/``.

This file can then be fed to `diceare-list` to create a wordlist
suitable for use with diceware.::

  $ python diceware_list.py /usr/share/dict/words
  !
  !!
  !!!
  ...
  alan
  alana
  alar
  ...
  zzz
  zzzz

By default lists of 8192 (=2**13) words are created. This value can be
changed with the `-l` option.

With `-n` you can tell `diceware_list` to put numbers into each line,
representing dice throws [#]_ ::


  $ python diceware_list.py -n -l 7776 /usr/share/dict/words
  11111 !
  11112 !!
  ...
  12353 alan
  12354 alana
  12355 alar
  ...
  66665 zzz
  66666 zzzz

See `--help` for other options.

`diceware_list` follows loosely the recommendations given on
http://diceware.com/ by Mr. Reinhold.


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


Coverage
--------

To get a coverage report, you can use the respective py.test plugin::

  (venv)$ pip install pytest-cov
  (venv)$ py.test --cov=diceware_list.py --cov-report=html

Skip the `--cov-report` option (or use `term` or `term-missing`
instead of `html`) to get a report on commandline.

.. [#] The wordlist length in this case should be
       ``(number-of-sides-per-dice)`` powered to
       ``(number-of-dicethrows)``, for instance 6**5 = 7776 for five
       six-sided dice or a single six-sided dice thrown five times.

.. _diceware: http://diceware.com/
.. _pip: https://pip.pypa.io/en/latest/
.. _py.test: https://pytest.org/
.. _virtualenv: https://virtualenv.pypa.io/
