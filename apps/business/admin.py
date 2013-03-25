from django.contrib import admin
from nnmware.apps.business.models import *
from django.utils.translation import ugettext_lazy as _
from nnmware.core.admin import TypeBaseAdmin, BaseSkillInline


class TypeEmployerProfileAdmin(TypeBaseAdmin):
    list_display = ('name', 'employer_type', 'is_radio', 'order_in_list', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('employer_type', '-is_radio', '-order_in_list', 'name')
    fieldsets = ((_("Type of employer profile"), {"fields": [('name', 'employer_type'),
                                                             ('order_in_list', 'is_radio'), ]}),)


class TypeEmployerOtherAdmin(TypeBaseAdmin):
    list_display = ('name', 'employer_type', 'is_radio')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    fieldsets = ((_("Type of other employer sphere"), {"fields": [('name', 'employer_type'), ]}),)


class TypeEmployerAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list', 'slug')
    fieldsets = (
        (_("Type of employer"), {"fields": [('name', 'order_in_list'),
        ]}),)
    ordering = ('-order_in_list', 'name',)


class AgencyAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Agency name"), {"fields": [('name'),
        ]}),)


admin.site.register(Agency, AgencyAdmin)
admin.site.register(TypeEmployer, TypeEmployerAdmin)
admin.site.register(TypeEmployerProfile, TypeEmployerProfileAdmin)
admin.site.register(TypeEmployerOther, TypeEmployerOtherAdmin)

