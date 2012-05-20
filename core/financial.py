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

