# -*- coding: utf-8 -*-
# nnmware(c)2012-2016
# Simple errors handlers

from __future__ import unicode_literals


class AccessError(Exception):
    pass


class UserIsDisabled(Exception):
    pass


class ShopError(Exception):
    pass


class EmptyDataError(Exception):
    pass
