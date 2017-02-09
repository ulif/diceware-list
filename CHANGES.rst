Changes
*******


1.0 (2017-02-09)
================

- The ``dicewarekit.txt`` list is not included in generated lists by
  default from now on. You can request inclusion with new option
  `use-kit`.  The old option `no-kit` is not supported any more.

- In numbered output, separate digits by ``-`` to distinguish numbers
  with more than one digit. Needed at least when generating wordlists
  for dice with more than 9 sides.

- Rename `-s` option to `-d` (as in ``dice-sides``).

- Logging output now registered under name `libwordlist`.

- Added new module `libwordlist` containing the API parts of `diceware-list`.

- New `--version` option.

- New `--prefix` option. If set prefix code is generated, i.e. lists that
  contain no item which is prefix of another list item.

- Claim support for Python 3.6.

- Restructure package: all single scripts are now part of a package.


0.3 (2016-07-25)
================

- Install script as `diceware-list` instead of `diceware_list`.

- Allow `--sides` option to support dice that do not have six sides.


0.2 (2016-03-18)
================

- Allow `-v` option multiple times for increased verbosity.

- Pick maximum width terms randomly. Until that change we included all
  shorter entries and additionally the (alphabetically) first entries
  of maximum width. Now, we pick a random set of these maximum width
  entries for the result list.

- Claim support for Python 3.5.


0.1 (2016-02-09)
================

- Initial release.
