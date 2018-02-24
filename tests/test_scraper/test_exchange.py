#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import choice
from re import findall as re_findall
from urllib.request import urlopen
from urllib.error import HTTPError

from tqdm import tqdm
import pytest

from pymarketcap import Pymarketcap, CoinmarketcapHTTPError
pym = Pymarketcap()

class TypeTester:
    def _currency(self, value): assert type(value) == str
    def _pair(self, value): assert type(value) == str
    def _vol_24h(self, value): assert type(value) in [float, type(None)]
    def _price(self, value): assert type(value) == float
    def _perc_volume(self, value): assert type(value) == float
    def _updated(self, value): assert type(value) == bool

tt = TypeTester()

def assert_types(res):
    assert type(res) == dict

    assert type(res["name"]) == str
    assert type(res["website"]) == str
    assert type(res["volume"]) in [float, type(None)]
    assert type(res["social"]) == dict

    for key, fields in res["social"].items():
        assert type(key) == str
        for field, data in fields.items():
            assert type(field) == str
            assert type(data) in [str, type(None)]

    for market in res["markets"]:
        assert type(market) == dict
        for key, value in market.items():
            eval("tt._{}({})".format(
                key,
                value if type(value) != str else '"%s"' % value
            ))

def test_types():
    exc = choice(pym.exchange_slugs)
    print("(Exchange: %s)" % exc, end=" ")
    assert_types(pym.exchange(exc))

def assert_number_of_markets(exc, markets):
    req = urlopen("https://coinmarketcap.com/exchanges/%s/" % exc)
    data = req.read()
    req.close()
    indexes = re_findall(r'<td class="text-right">(\d+)</td>', data.decode())
    assert len(markets) == int(indexes[-1])

def assert_consistence(res, exc):
    assert len(res["name"]) > 0
    assert res["name"] != None
    assert len(res["website"]) > 0
    assert res["website"] != None
    assert_number_of_markets(exc, res["markets"])

def test_consistence():
    exc = choice(pym.exchange_slugs)
    print("(Exchange: %s)" % exc, end=" ")
    assert_types(pym.exchange(exc))


def test_convert():
    exc = choice(pym.exchange_slugs)
    print("(Exchange: %s)" % exc, end=" ")
    res = pym.exchange(exc, convert="BTC")

    assert_types(res)
    assert_consistence(res, exc)

def test_invalid():
    exc = "OkCoin Intl."
    try:
        with pytest.raises(ValueError) as excinfo:
            pym.exchange(exc)
        assert '%s is not a valid exchange name.' % exc in str(excinfo.value)
    except HTTPError:
        pass

@pytest.mark.end2end
def test_end2end():
    for exc in tqdm(pym.exchange_slugs, desc="Testing all_exchanges"):
        tqdm.write(exc)
        for convert in ["USD", "BTC"]:
            res = pym.exchange(exc, convert=convert)
            assert_types(res)
            assert_consistence(res, exc)
