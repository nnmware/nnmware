# nnmware(c)2012-2021

from __future__ import unicode_literals

from django.dispatch import Signal

action = Signal(['user', 'verb', 'action_object', 'target', 'description', 'timestamp'])


# Signal for create new notice
notice = Signal(['user', 'sender', 'verb', 'target', 'description', 'notice_type'])
