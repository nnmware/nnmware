from django.core.management.base import BaseCommand, CommandError
from nnmware.core.parsers import parse_currency
from datetime import datetime

class Command(BaseCommand):
#    args = '<poll_id poll_id ...>'
    help = 'Parsed Currency Rate from CBR site'

    def handle(self, *args, **options):
	print 'Trying parce currency on date %s' % datetime.now()
	parse_currency()
	print 'Succesfully parce currency on date %s' % datetime.now()
