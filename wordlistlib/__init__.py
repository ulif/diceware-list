# -*- coding: utf-8 -*-
#  wordlistlib -- tools for generating wordlists
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

def base10_to_n(num, base):
    """Turn base-10 integer `num` into base-`base` form.

    Returns a list of numbers representing digits in `base`.

    For instance in base-2 we have only the digits ``0`` and
    ``1``. Turning the base-10 integer ``5`` into a base-2 number
    results in ``101`` or, as a list, in::

        >>> base10_to_n(5, base=2)
        [1, 0, 1]

    The result list represents the single "digits" of a differently
    based number. This holds also for 'digits' >= 10::

        >>> base10_to_n(127, base=16)
        [7, 15]

    which in hexadecimal notation would normally read ``0x7F``.
    """
    result = []
    curr = num
    while curr >= base:
        curr, digit = divmod(curr, base)
        result.append(digit)
    result.append(curr)
    result.reverse()
    return result
