from django.contrib import admin
from nnmware.apps.money.models import *
from django.utils.translation import ugettext_lazy as _


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user','date','actor','status','amount','currency')
    search_fields = ('name',)
    list_filter = ('user','date')
    ordering = [('user'),]
    readonly_fields = ('content_type','object_id')
    fieldsets = (
        (_("Transaction"), {"fields": [("user","date"),
            ('amount','currency','status'),
            ('content_type','object_id')]}),)


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code',)
    search_fields = ('name',)

class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('currency','date','rate')
    search_fields = ('currency',)

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(ExchangeRate, ExchangeRateAdmin)
