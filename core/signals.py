# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.dispatch import Signal

action = Signal(providing_args=['user', 'verb', 'action_object', 'target', 'description', 'timestamp'])

# Signal for create new notice
notice = Signal(providing_args=['user', 'sender', 'verb', 'target', 'description', 'notice_type'])

