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

"""wordlistlib -- a library for wordlist-related operations.
"""
from __future__ import unicode_literals
import unicodedata

DICE_SIDES = 6  # we normally handle 6-sided dice.


def normalize(text):
    """Normalize text.
    """
    TRANSFORMS = {
        'ä': 'ae', 'Ä': 'AE', "æ": 'ae', "Æ": 'AE',
        'ö': 'oe', 'Ö': 'OE', "ø": 'oe', "Ø": 'OE',
        "ü": 'UE', "Ü": 'UE',
        'ß': 'ss'
    }
    transformed = "".join([TRANSFORMS.get(x, x) for x in text])
    nfkd_form = unicodedata.normalize("NFKD", transformed)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


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


def idx_to_dicenums(
        item_index, dice_num, dice_sides=DICE_SIDES, separator='-'):
    """Get a set of dicenums for list item numbers.

    Turn an index number of a list item into a number of dice numbers
    representing this index. The dicenums are returned as a string like
    ``"1-2-2-6-2-5"``.

    `item_index` is the index number of some item.

    `dice_num` is the number of (n-sided) dice used.

    `dice_sides` is the number of sides per die.

    `separator` is the string to separate the result numbers.

    Example: we have two dice resulting in 36 possible combinations. If
    first possible combination is "1-1", second one "1-2" and so on,
    then we have a mapping from indexes 1..36 to dice combinations (from
    "1-1" up to "6-6").

    For a reasonable result, we expect

      0 <= `item_index` < `dice_num` ** `dice_sides`.

    Some examples::

        >>> print(idx_to_dicenums(0, 1))
        1
        >>> print(idx_to_dicenums(5, 1))
        6
        >>> print(idx_to_dicenums(0, 3))
        1-1-1
        >>> print(idx_to_dicenums(5, 3))
        1-1-6

    We are not restricted to (6-sided) dice. If we throw a (2-sided)
    coin 3 times, we have an index range from ``0`` to ``2^3 = 8``
    (there are 8 possible combinations of coin throws). Index ``5``
    then computes to::

        >>> print(idx_to_dicenums(5, 3, 2))
        2-1-2

    If `dice_sides` < 10, you can generate compressed output by leaving
    the separator out::

        >>> print(idx_to_dicenums(5, 3, 2, separator=""))
        212

    """
    nums = [x+1 for x in base10_to_n(item_index, dice_sides)]
    padded = [1, ] * dice_num + nums
    return separator.join(["%s" % x for x in padded[-dice_num:]])
