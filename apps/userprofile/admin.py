from django.contrib import admin
from nnmware.apps.userprofile.models import Profile
from django.utils.translation import ugettext_lazy as _


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', )
    list_filter = ('user',)
    search_fields = ('user__username', 'user__first_name')
    fieldsets = (
        (_("Main"), {"fields": [("user", "gender", "birthdate"),
            ('about', 'signature', 'show_signatures', 'time_zone')]}),
        (_("Addons"), {"fields": [('website', 'icq', 'skype', 'jabber'),
            ('mobile', 'workphone', 'publicmail'),
            ('facebook', 'googleplus', 'twitter','avatar'),
            ]}),)

admin.site.register(Profile, ProfileAdmin)


