# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal
from time import localtime, strftime
import urllib2
import xml.dom.minidom

#---------------------------------------------------------------------------
from django.conf import settings

def CurrencyXMLInput(sDate):
    cURL="http://www.cbr.ru/scripts/XML_daily.asp?date_req=%s" % (sDate)
    u=urllib2.urlopen(cURL)
    return u.read()

#---------------------------------------------------------------------------
def ParseXMLCurrency(xmlDoc):
    lstDicXMLNodes=[]
    dicXMLNodes={}
    xmldoc=xml.dom.minidom.parseString(xmlDoc)
    root=xmldoc.documentElement
    for valute in root.childNodes:
        if valute.nodeName=='#text':
            continue
        for ch in valute.childNodes:
            if ch.nodeName=='#text': # Drop TextNode, that is means "\n" in the xml document
                continue
            dicXMLNodes[ch.nodeName]=ch.childNodes[0].nodeValue
        lstDicXMLNodes.append(dicXMLNodes)
        dicXMLNodes={}
    return lstDicXMLNodes

#---------------------------------------------------------------------------
def parse_currency(on_date=None):
    f = lambda x: Decimal(x.replace(',','.'))
    sDate= on_date or strftime("%d.%m.%Y", localtime())
    d, m, y = map(lambda x: int(x), sDate.split('.'))
    rate_date = datetime.date(y, m, d)
    lstCurrency=ParseXMLCurrency(CurrencyXMLInput(sDate))
    from nnmware.apps.money.models import ExchangeRate, Currency
    currencies = Currency.objects.all().values_list('code',flat=True)
    for currency in lstCurrency:
        charcode = currency['CharCode']
        if charcode in currencies and charcode <> settings.DEFAULT_CURRENCY:
            curr = Currency.objects.get(code=charcode)
            try:
                rate = ExchangeRate.objects.get(date=rate_date, currency=curr)
            except :
                rate = ExchangeRate()
                rate.date= rate_date
                rate.currency=curr
            rate.nominal = currency['Nominal']
            rate.official_rate = f(currency['Value'])
            if not rate.rate:
                rate.rate = f(currency['Value'])
            rate.save()
    return None

