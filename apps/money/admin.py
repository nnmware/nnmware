# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.money.models import Transaction, Bill, Currency, ExchangeRate


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'actor', 'status', 'amount', 'currency', 'content_object')
    search_fields = ('name', )
    list_filter = ('user', 'date')
    ordering = ('user', )
#    readonly_fields = ('actor_ctype','actor_oid','target_ctype','target_oid')
    fieldsets = (
        (_("Transaction"), {"fields": [("user", "date"),
            ('amount', 'currency', 'status'),
            ('actor_ctype', 'actor_oid'),
            ('content_type', 'object_id')]}),)

    _readonly_fields = []  # Default fields that are readonly for everyone.

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self._readonly_fields)
        if request.user.is_staff and not request.user.is_superuser:
            readonly.extend(['user', 'date', 'actor_ctype', 'actor_oid', 'content_type', 'object_id', 'amount',
                             'currency', 'status'])
        return readonly


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_billed', 'content_object', 'status', 'amount', 'currency')
    search_fields = ('name',)
    list_filter = ('user', 'date_billed')
    ordering = ('user', )
    # readonly_fields = ('target_ctype','target_oid')
    fieldsets = (
        (_("Bill"), {"fields": [("user", "date_billed"),
            ('amount', 'currency'),
            ('content_type', 'object_id'),
            ('description_small',),
            ('description',),
            ('status', 'date')]}),)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code',)
    search_fields = ('name',)


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('currency', 'date', 'nominal', 'official_rate', 'rate')
    search_fields = ('currency',)
    fieldsets = (
        (_("Exchange Rate"), {"fields": [("currency", "date"),
            ('nominal', 'official_rate', 'rate'), ]}),)
