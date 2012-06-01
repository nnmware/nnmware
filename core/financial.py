from datetime import datetime
from nnmware.apps.money.models import ExchangeRate, Currency
from nnmware.core.config import OFFICIAL_RATE, CURRENCY

def convert_from_client_currency(request, amount):
    try:
        if request.COOKIES['currency'] == CURRENCY:
            return amount
        currency = Currency.objects.get(code=request.COOKIES['currency'])
        rate = ExchangeRate.objects.filter(currency=currency).filter(date__lte=datetime.now()).order_by('-date')[0]
        if OFFICIAL_RATE:
            exchange = rate.official_rate
        else:
            exchange = rate.rate
        return int((int(amount)*exchange)/rate.nominal)
    except :
        return int(amount)

def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10

def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0
