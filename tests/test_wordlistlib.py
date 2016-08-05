# -*- coding: utf-8 -*-
#  diceware_list -- generate wordlists for diceware
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

# Tests for wordlistlib module

from wordlistlib import base10_to_n, idx_to_dicenums


def test_base10_to_n():
    # we can turn integers into n-based numbers
    assert base10_to_n(0, 2) == [0]
    assert base10_to_n(1, 2) == [1]
    assert base10_to_n(2, 2) == [1, 0]
    assert base10_to_n(3, 2) == [1, 1]
    assert base10_to_n(7775, 6) == [5, 5, 5, 5, 5]
    assert base10_to_n(0, 6) == [0, ]
    assert base10_to_n(1, 6) == [1, ]
    assert base10_to_n(6, 6) == [1, 0]
    assert base10_to_n(34, 6) == [5, 4]
    assert base10_to_n(35, 6) == [5, 5]
    assert base10_to_n(37, 6) == [1, 0, 1]
    assert base10_to_n(38, 6) == [1, 0, 2]
    assert base10_to_n(255, 16) == [15, 15]
    assert base10_to_n(256, 16) == [1, 0, 0]

def test_idx_to_dicenums():
    # we can get dice numbers from list indexes
    assert idx_to_dicenums(0, 5) == "1-1-1-1-1"
    assert idx_to_dicenums(1, 5) == "1-1-1-1-2"
    assert idx_to_dicenums(7774, 5) == "6-6-6-6-5"
    assert idx_to_dicenums(7775, 5) == "6-6-6-6-6"
    # different dice sides, different results
    assert idx_to_dicenums(0, 4, 4) == "1-1-1-1"
    assert idx_to_dicenums(255, 4, 4) == "4-4-4-4"
    assert idx_to_dicenums(255, 4) == "2-2-1-4"
    # we can change the separator string (or leave it out)
    assert idx_to_dicenums(0, 3) == "1-1-1"  # default
    assert idx_to_dicenums(0, 3, separator="sep") == "1sep1sep1"
    assert idx_to_dicenums(0, 3, separator="") == "111"
