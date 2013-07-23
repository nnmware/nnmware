# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from nnmware.core.parsers import parse_currency


class Command(BaseCommand):
    help = 'Parsed Currency Rate from CBR site'

    def handle(self, *args, **options):
        #print 'Trying parce currency on date %s' % datetime.now()
        parse_currency()
        #print 'Succesfully parce currency on date %s' % datetime.now()
