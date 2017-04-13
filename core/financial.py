# nnmware(c)2012-2017

from __future__ import unicode_literals
from datetime import datetime, date, time
from io import StringIO

from django.http import HttpResponse
from django.utils.timezone import now

from nnmware.core.utils import setting
from nnmware.apps.money.models import ExchangeRate, Currency


def convert_from_client_currency(request, amount):
    # noinspection PyBroadException
    try:
        if request.COOKIES['currency'] == setting('CURRENCY', 'RUB'):
            return amount
        currency = Currency.objects.get(code=request.COOKIES['currency'])
        rate = ExchangeRate.objects.filter(currency=currency).filter(date__lte=now()).order_by('-date')[0]
        if setting('OFFICIAL_RATE', True):
            exchange = rate.official_rate
        else:
            exchange = rate.rate
        return int((int(amount) * exchange) / rate.nominal)
    except:
        return int(amount)


def luhn_checksum(card_number):
    def digits_of(n):
        return [int(dig) for dig in str(n)]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10


def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0


class ExcelResponse(HttpResponse):
    def __init__(self, data, output_name='excel_data', headers=None, force_csv=False, encoding='utf8'):
        # Make sure we've got the right type of data to work with
        valid_data = False
        data = list(data.values())
        if hasattr(data, '__getitem__'):
            if isinstance(data[0], dict):
                if headers is None:
                    headers = data[0].keys()
                data = [[row[col] for col in headers] for row in data]
                data.insert(0, headers)
            if hasattr(data[0], '__getitem__'):
                valid_data = True
        assert valid_data is True, "ExcelResponse requires a sequence of sequences"
        output = StringIO()
        # Excel has a limit on number of rows; if we have more than that, make a csv
        use_xls = False
        if len(data) <= 65536 and force_csv is not True:
            use_xls = True
        if use_xls:
            import xlwt
            book = xlwt.Workbook(encoding=encoding)
            sheet = book.add_sheet('Sheet 1')
            styles = {'datetime': xlwt.easyxf(num_format_str='yyyy-mm-dd hh:mm:ss'),
                      'date': xlwt.easyxf(num_format_str='yyyy-mm-dd'),
                      'time': xlwt.easyxf(num_format_str='hh:mm:ss'),
                      'default': xlwt.Style.default_style}

            for rowx, row in enumerate(data):
                for colx, value in enumerate(row):
                    if isinstance(value, datetime):
                        cell_style = styles['datetime']
                    elif isinstance(value, date):
                        cell_style = styles['date']
                    elif isinstance(value, time):
                        cell_style = styles['time']
                    else:
                        cell_style = styles['default']
                    sheet.write(rowx, colx, value, style=cell_style)
            book.save(output)
            content_type = 'application/vnd.ms-excel'
            file_ext = 'xls'
        else:
            for row in data:
                out_row = []
                for value in row:
                    value = value.encode(encoding)
                    out_row.append(value.replace('"', '""'))
                output.write('"%s"\n' % '","'.join(out_row))
            content_type = 'text/csv'
            file_ext = 'csv'
        output.seek(0)
        super(ExcelResponse, self).__init__(content=output.getvalue(), content_type=content_type)
        self['Content-Disposition'] = 'attachment;filename="%s.%s"' % (output_name.replace('"', '\"'), file_ext)
