Changes
*******

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
