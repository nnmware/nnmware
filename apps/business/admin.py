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


class CompanyAdmin(admin.ModelAdmin):
    model = Company
    list_display = ('name', 'region', 'work_on', 'work_off')
    list_filter = ('name', 'region', )
    search_fields = ('name', 'position')
    fieldsets = (
        (_("Employer"), {"fields": [
            ("name", 'fullname'), ('category', 'region',),
            ('description', ),
            ('work_on', 'work_off'),
            ('phone_on', 'phone_off')
        ]}),
        (_("Sphere of activity"), {"classes": ("collapse closed",), "fields": [
            ('employer_profile',),
            ('employer_other',),
            ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en", 'fullname_en'), ("description_en",)]})
    )
    ordering = ('region', 'name')


admin.site.register(Agency, AgencyAdmin)
admin.site.register(TypeEmployer, TypeEmployerAdmin)
admin.site.register(TypeEmployerProfile, TypeEmployerProfileAdmin)
admin.site.register(TypeEmployerOther, TypeEmployerOtherAdmin)
admin.site.register(CompanyCategory, CompanyCategoryAdmin)
admin.site.register(Company, CompanyAdmin)
