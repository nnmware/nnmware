# nnmware(c)2012-2016

from __future__ import unicode_literals
import datetime
from decimal import Decimal
from time import localtime, strftime
from urllib.request import urlopen
import xml.dom.minidom

from nnmware.core.utils import setting


def currency_xml_input(sdate):
    c_url = "http://www.cbr.ru/scripts/XML_daily.asp?date_req=%s" % sdate
    u = urlopen(c_url)
    return u.read()


def parse_xml_currency(xml_doc):
    lst_dic_xml_nodes = []
    dic_xml_nodes = {}
    xmldoc = xml.dom.minidom.parseString(xml_doc)
    root = xmldoc.documentElement
    for valute in root.childNodes:
        if valute.nodeName == '#text':
            continue
        for ch in valute.childNodes:
            if ch.nodeName == '#text':  # Drop TextNode, that is means "\n" in the xml document
                continue
            dic_xml_nodes[ch.nodeName] = ch.childNodes[0].nodeValue
        lst_dic_xml_nodes.append(dic_xml_nodes)
        dic_xml_nodes = {}
    return lst_dic_xml_nodes


def parse_currency(on_date=None):
    f = lambda x: Decimal(x.replace(',', '.'))
    sdate = on_date or strftime("%d.%m.%Y", localtime())
    d, m, y = map(lambda x: int(x), sdate.split('.'))
    rate_date = datetime.date(y, m, d)
    lst_currency = parse_xml_currency(currency_xml_input(sdate))
    from nnmware.apps.money.models import ExchangeRate, Currency
    currencies = Currency.objects.all().values_list('code', flat=True)
    for currency in lst_currency:
        charcode = currency['CharCode']
        if charcode in currencies and charcode != setting('DEFAULT_CURRENCY', 'RUB'):
            curr = Currency.objects.get(code=charcode)
            # noinspection PyBroadException
            try:
                rate = ExchangeRate.objects.get(date=rate_date, currency=curr)
            except:
                rate = ExchangeRate()
                rate.date = rate_date
                rate.currency = curr
            rate.nominal = currency['Nominal']
            rate.official_rate = f(currency['Value'])
            if not rate.rate:
                rate.rate = f(currency['Value'])
            rate.save()
    return None
