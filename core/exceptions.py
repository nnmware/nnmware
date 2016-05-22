# nnmware(c)2012-2016

from __future__ import unicode_literals


class AccessError(Exception):
    pass


class UserIsDisabled(Exception):
    pass


class MarketError(Exception):
    pass


class EmptyDataError(Exception):
    pass
