# -*- coding: utf-8 -*-
from __future__ import unicode_literals

class AccessError(Exception):
    pass


class UserIsDisabled(Exception):
    pass


class ShopError(Exception):
    pass


class EmptyDataError(Exception):
    pass
