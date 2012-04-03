
from ConfigParser import RawConfigParser
from django.conf import settings

config = RawConfigParser()
config.read(settings.NNMWARE_INI_FILE)

ENGINE_DEBUG = config.getboolean('engine','DEBUG')

CURRENCY = config.get('money', 'DEFAULT_CURRENCY')
OFFICIAL_RATE = config.getboolean('money', 'OFFICIAL_RATE')
