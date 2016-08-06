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
from __future__ import unicode_literals
import random
from wordlistlib import (
    base10_to_n, idx_to_dicenums, normalize, shuffle_max_width_items)


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


def test_idx_to_dicenums_gives_text():
    # we get text from this function, i.e. unicode under py2.
    result = idx_to_dicenums(0, 5)
    assert isinstance(result, type('text'))


def test_normalize():
    # we can normalize texts.
    assert normalize("ªºÀÁÂÃÄÅÆ") == "aoAAAAAEAAE"
    assert normalize("ÇÈÉÊËÌÍÎÏ") == "CEEEEIIII"
    assert normalize("ÒÓÔÕÖØÙÚÛÜ") == "OOOOOEOEUUUUE"
    # "ÐÑÝßàáâãäåæçèéêëìíîïñòóôõöøùúûüý"
    # "þÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİ"
    # "ıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖŗŘřŚśŜŝŞşŠšŢţ"
    # "ŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽžſƀƁƂƃƄƅƆƇƈƉƊƋƌƍ"
    assert normalize("mäßig") == "maessig"


def test_normalize_gives_text():
    # we get unicode/text strings back
    assert isinstance(normalize("far"), type("text"))
    assert isinstance(normalize("fär"), type("text"))
    assert isinstance(normalize(str("far")), type("text"))


def test_shuffle_max_width_items(monkeypatch):
        # we can shuffle the max width items of a list
        # install a pseudo-shuffler that generates predictable orders
        monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
        in_list = ["a", "aa", "bb", "cc"]
        result = list(shuffle_max_width_items(in_list))
        # last elements are returned in reverse order.
        assert result == ["a", "cc", "bb", "aa"]


def test_shuffle_max_width_items_unsorted_input(monkeypatch):
        # we can shuffle the max width items of an unsorted list
        # install a pseudo-shuffler that generates predictable orders
        monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
        in_list = ["aa", "d", "bb", "a", "cc"]
        result = list(shuffle_max_width_items(in_list))
        # last elements are returned in reverse order.
        assert result == ["d", "a", "cc", "bb", "aa"]


def test_shuffle_max_width_items_drop_over_max_width(monkeypatch):
        # with a given max_width we drop words that are longer
        monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
        in_list = ["eeee", "bb", "ccc", "aa", "ddd"]
        result = list(shuffle_max_width_items(in_list, max_width=3))
        assert "eeee" not in result
