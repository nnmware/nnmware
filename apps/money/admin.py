from django.contrib import admin
from nnmware.apps.money.models import *
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.money.models import Account


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user','date','actor','status','amount','currency','target')
    search_fields = ('name',)
    list_filter = ('user','date')
    ordering = [('user'),]
    readonly_fields = ('actor_ctype','actor_oid','target_ctype','target_oid')
    fieldsets = (
        (_("Transaction"), {"fields": [("user","date"),
            ('amount','currency','status'),
            ('actor_ctype','actor_oid'),
            ('target_ctype','target_oid')]}),)

class AccountAdmin(admin.ModelAdmin):
    list_display = ('user','date','target','status','amount','currency')
    search_fields = ('name',)
    list_filter = ('user','date')
    ordering = [('user'),]
    readonly_fields = ('target_ctype','target_oid')
    fieldsets = (
        (_("Account"), {"fields": [("user","date"),
            ('amount','currency','status'),
            ('target_ctype','target_oid')]}),)

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code',)
    search_fields = ('name',)

class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('currency','date','rate')
    search_fields = ('currency',)

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(ExchangeRate, ExchangeRateAdmin)
admin.site.register(Account, AccountAdmin)
