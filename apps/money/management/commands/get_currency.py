# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from nnmware.core.parsers import parse_currency


class Command(BaseCommand):
    help = 'Parsed Currency Rate from CBR site'

    def handle(self, *args, **options):
        # print 'Trying parse currency on date %s' % now()
        parse_currency()
        # print 'Succesfully parse currency on date %s' % now()
