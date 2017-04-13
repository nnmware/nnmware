# nnmware(c)2012-2017

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.business.models import TypeEmployerProfile, TypeEmployerOther, TypeEmployer, Agency, \
    CompanyCategory, CompanyDetail, Company, VacancyCategory, Vacancy
from nnmware.core.admin import TypeBaseAdmin, TreeAdmin


@admin.register(TypeEmployerProfile)
class TypeEmployerProfileAdmin(TypeBaseAdmin):
    list_display = ('name', 'employer_type', 'is_radio', 'position', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('employer_type', '-is_radio', 'position', 'name')
    fieldsets = ((_("Type of employer profile"), {"fields": [('name', 'employer_type'),
                                                             ('position', 'is_radio'), ]}),)


@admin.register(TypeEmployerOther)
class TypeEmployerOtherAdmin(TypeBaseAdmin):
    list_display = ('name', 'employer_type', 'is_radio')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    fieldsets = ((_("Type of other employer sphere"), {"fields": [('name', 'employer_type'), ]}),)


@admin.register(TypeEmployer)
class TypeEmployerAdmin(TypeBaseAdmin):
    list_display = ('name', 'position', 'slug')
    fieldsets = (
        (_("Type of employer"), {"fields": [('name', 'position'), ]}),)
    ordering = ('position', 'name',)


@admin.register(Agency)
class AgencyAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Agency name"), {"fields": [('name', ), ]}),)


@admin.register(CompanyCategory)
class CompanyCategoryAdmin(TreeAdmin):
    fieldsets = (
        (_("Main"), {"fields": [("name", "slug"), ("parent",
                                                   "login_required",)]}),
        (_("Description"), {"classes": ("collapse",),
                            "fields": [("description",), ("position", "rootnode"), ('admins', )]}),
    )


class CompanyDetailInline(admin.StackedInline):
    model = CompanyDetail
    fieldsets = (
        (_("Company Data"), {"fields": [
            ('inn', 'ogrn'), ('kpp', 'kpp_add'),
            ('okato', 'okpo'),
            ('num_cert_state_reg', 'date_state_reg'),
            ('authority_state_reg', ),
            ('date_ogrn', 'authority_ogrn')
        ]}),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    model = Company
    list_display = ('name', 'region', 'work_on', 'work_off')
    list_filter = ('name', 'region', )
    search_fields = ('name', 'w_position')
    fieldsets = (
        (_("Employer"), {"fields": [
            ("name", 'fullname'), ('main_category', 'category'), ('branch', 'parent'),
            ('description', ),
            ('work_on', 'work_off'),
            ('phone_on', 'phone_off')
        ]}),
        (_("Sphere of activity"), {"classes": ("collapse",), "fields": [
            ('employer_profile',),
            ('employer_other',)]}),
        (_("Address"), {"classes": ("collapse",),
                        "fields": [("country", 'region'), ('city', 'zipcode'), ('street', 'stationmetro'),
                                   ('house_number', 'building'), ('flat_number',), ('longitude', 'latitude')]}),
        (_("English"), {"classes": ("collapse",),
                        "fields": [("name_en", 'fullname_en'), ('teaser_en', ), ("description_en",)]}))
    ordering = ('region', 'name')
    inlines = [CompanyDetailInline, ]


@admin.register(VacancyCategory)
class VacancyCategoryAdmin(TreeAdmin):
    fieldsets = (
        (_("Main"), {"fields": [("name", "slug"), ("parent",
                                                   "login_required",)]}),
        (_("Description"), {"classes": ("collapse",),
                            "fields": [("description",), ("position", "rootnode"), ('admins', )]}),
    )


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('name', 'vacancy_type', 'user', 'company', 'enabled')
    fieldsets = (
        (_("Vacancy"), {"fields": [
            ("name", 'vacancy_type'), ('category', ), ('user', 'company'),
            ('description', ),
            ('teaser', ),
            ('created_date', 'updated_date')
        ]}),
        (_("English"), {"classes": ("collapse",),
                        "fields": [("name_en", ), ("description_en",)]}))
    ordering = ('-created_date', 'name')
