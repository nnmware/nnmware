from django.contrib import admin
from nnmware.apps.business.models import *
from django.utils.translation import ugettext_lazy as _
from nnmware.core.admin import TypeBaseAdmin, TreeAdmin


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
        (_("Type of employer"), {"fields": [('name', 'order_in_list'), ]}),)
    ordering = ('-order_in_list', 'name',)


class AgencyAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Agency name"), {"fields": [('name', ), ]}),)


class CompanyCategoryAdmin(TreeAdmin):
    fieldsets = (
        (_("Main"), {"fields": [("name", "slug"), ("parent",
                                                   "login_required",)]}),
        (_("Description"), {"classes": ("collapse",),
                            "fields": [("description",), ("ordering", "rootnode"), ('admins', )]}),
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


class CompanyAdmin(admin.ModelAdmin):
    model = Company
    list_display = ('name', 'region', 'work_on', 'work_off')
    list_filter = ('name', 'region', )
    search_fields = ('name', 'position')
    fieldsets = (
        (_("Employer"), {"fields": [
            ("name", 'fullname'), ('main_category', 'category'), ('branch', 'parent'),
            ('description', ),
            ('work_on', 'work_off'),
            ('phone_on', 'phone_off')
        ]}),
        (_("Sphere of activity"), {"classes": ("grp-collapse grp-closed",), "fields": [
            ('employer_profile',),
            ('employer_other',)]}),
        (_("Address"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("country", 'region'),
                                   ('city', 'zipcode'),
                                   ('street', 'stationmetro'),
                                   ('house_number', 'building'), ('flat_number', ),
                                   ('longitude', 'latitude')
                        ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en", 'fullname_en'), ('teaser_en', ), ("description_en",)]}))
    ordering = ('region', 'name')
    inlines = [CompanyDetailInline, ]


class VacancyCategoryAdmin(TreeAdmin):
    fieldsets = (
        (_("Main"), {"fields": [("name", "slug"), ("parent",
                                                   "login_required",)]}),
        (_("Description"), {"classes": ("collapse",),
                            "fields": [("description",), ("ordering", "rootnode"), ('admins', )]}),
    )


class VacancyAdmin(admin.ModelAdmin):
    list_display = ('name', 'vacancy_type', 'user', 'company', 'enabled')
    fieldsets = (
        (_("Vacancy"), {"fields": [
            ("name", 'vacancy_type'), ('category', ), ('user', 'company'),
            ('description', ),
            ('teaser', ),
            ('created_date', 'updated_date')
        ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en", ), ("description_en",)]}))
    ordering = ('-created_date', 'name')


admin.site.register(Agency, AgencyAdmin)
admin.site.register(TypeEmployer, TypeEmployerAdmin)
admin.site.register(TypeEmployerProfile, TypeEmployerProfileAdmin)
admin.site.register(TypeEmployerOther, TypeEmployerOtherAdmin)
admin.site.register(CompanyCategory, CompanyCategoryAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(VacancyCategory, VacancyCategoryAdmin)
admin.site.register(Vacancy, VacancyAdmin)
