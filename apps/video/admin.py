from django.contrib import admin
from nnmware.apps.video.models import Video
from django.utils.translation import ugettext_lazy as _


class VideoAdmin(admin.ModelAdmin):
    list_display = ('user','project_name','slug' )
    list_filter = ('user','project_name')
    search_fields = ('user__username', 'user__first_name')
    filter_horizontal = ['tags']
    fieldsets = (
        (_("Main"), {"fields": [("user", "project_name"),
            ('project_url', 'video_url')]}),
        (_("Addons"), {"fields": [('description', 'login_required', 'slug'),
            ('thumbnail')]}),
        (_("Tags"), {"classes": ("grp-collapse grp-closed",), "fields": [
            ('tags')]}),

        )

admin.site.register(Video, VideoAdmin)
