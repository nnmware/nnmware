from django.contrib import admin
from nnmware.apps.video.models import Video
from django.utils.translation import ugettext_lazy as _


class VideoAdmin(admin.ModelAdmin):
    list_display = ('project_name','user','slug','description' )
    list_filter = ('user','project_name')
    search_fields = ('user__username', 'user__first_name')
    filter_horizontal = ['tags','users_viewed']
    fieldsets = (
        (_("Main"), {"fields": [("user", "project_name"),
            ('project_url', 'video_url')]}),
        (_("Addons"), {"fields": [('description'), ('login_required', 'slug'),
            ('thumbnail')]}),
        (_("Tags"), {"classes": ("grp-collapse grp-closed",), "fields": [
            ('tags')]}),
        (_("Users viewed"), {"classes": ("grp-collapse grp-closed",), "fields": [
            ('users_viewed')]}),
        )

admin.site.register(Video, VideoAdmin)
