from copy import deepcopy
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.forms.fields import ChoiceField
from django.forms.models import ModelForm, ModelChoiceField
from nnmware.core.models import JComment, Doc, Pic, Tag, Action, Follow, Notice, Message, VisitorHit
from django.utils.translation import ugettext_lazy as _


class JCommentAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('nnmware'), {'fields': [('parent', 'content_type', 'object_id')]}),
        (_('Content'), {'fields': [('comment', 'user', 'status')]}),
        (_('Meta'), {'fields': [('publish_date', 'updated_date',
                                 'ip')]}),
        )
    list_display = ('user', 'publish_date', 'content_type',
                    'parent', '__unicode__')
    list_filter = ('publish_date',)
    date_hierarchy = 'publish_date'
    search_fields = ('comment', 'user__username')

admin.site.register(JComment, JCommentAdmin)


class TreeAdmin(admin.ModelAdmin):
    list_display = ('title', '_parents_repr', 'status', 'rootnode', 'user')
    list_display_links = ("title",)
    list_editable = ("status",)
    list_filter = ("status",)
    ordering = ['parent__id', 'title']
    prepopulated_fields = {'slug': ('title',)}
    actions = None
    search_fields = ("title", )
    date_hierarchy = "publish_date"
    fieldsets = (
        (_("Main"), {"fields": [("title", "slug", "parent"), ("publish_date",
                    "user", "status", "login_required")]}),
        (_("Description"), {"classes": ("collapse",),
                "fields": [("description", "ordering", "rootnode"), ]}),
        )


class MetaDataAdmin(admin.ModelAdmin):
    """
     Admin class for subclasses of the abstract ``Displayable`` model.
     """
    prepopulated_fields = {'slug': ('title',)}
    list_display = ("title", "status", "admin_link")
    list_display_links = ("title",)
    list_editable = ("status",)
    list_filter = ("status",)
    search_fields = ("title", "content",)
    date_hierarchy = "publish_date"
    fieldsets = (
        (_("Main"), {"fields": [("title", "slug", "status", "user"), ]}),
        (_("Description"), {"fields": [("description", "publish_date",
                    "allow_comments"), ]}),
        )

    def save_form(self, request, form, change):
        """
          Set the object's owner as the logged in user.
          """
        obj = form.save(commit=False)
        if obj.user is None:
            obj.user = request.user
        return super(MetaDataAdmin, self).save_form(request, form, change)

    def queryset(self, request):
        """
          Filter the change list by currently logged in user if not a
          superuser.
          """
        qs = super(MetaDataAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user__id=request.user.id)


class DocAdmin(admin.ModelAdmin):
    """
     Admin class for Doc.
     """
#    readonly_fields = ('file',)
    fieldsets = (
        (_('nnmware'), {'fields': [('user', 'content_type', 'object_id')]}),
        (_('Doc'), {'fields': [('file', 'publish_date', 'ordering')]}),
        (_('Meta'), {'fields': [('description', 'filetype')]}),
        )
    list_display = ("description", "file", "publish_date", "user",
            "locked", "size", "admin_link")


class PicAdmin(admin.ModelAdmin):
 #   readonly_fields = ('pic',)
    fieldsets = (
        (_('nnmware'), {'fields': [('user', 'content_type', 'object_id')]}),
        (_('Pic'), {'fields': [('pic', 'publish_date')]}),
        (_('Meta'), {'fields': [('description', 'source')]}),
        )
    list_display = ('user', 'publish_date', 'content_type',
                    'pic', '__unicode__')
    list_filter = ('publish_date',)
    date_hierarchy = 'publish_date'
    search_fields = ('description', 'user__username')

class VisitorHitAdmin(admin.ModelAdmin):
    readonly_fields = ('user','date','ip_address','session_key','user_agent','referrer',
        'url','secure','hostname')
    fieldsets = (
        (_('Visitor hit'), {'fields': [('user', 'date','secure'),
            ('ip_address', 'session_key'),
            ('user_agent', 'referrer'),
            ('url','hostname'),
        ]}),
        )
    list_display = ('user', 'date', 'ip_address',
                    'user_agent','url','secure')
    list_filter = ('date','user')
    search_fields = ('user__username', 'user_agent')
    ordering = ('-date','user','ip_address')

class TagAdmin(admin.ModelAdmin):
    fieldsets = ((_('nnmware'), {'fields': [('name','slug')]}),)
    list_display = ('name','slug')

class ActionAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('user', 'verb', 'content_object','timestamp','ip','user_agent')
    list_filter = ('timestamp',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'user', 'actor')
    list_editable = ('user',)
    list_filter = ('user',)

class NoticeAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'verb', 'sender','ip','user_agent')
    list_filter = ('user',)

class MessageAdminForm(ModelForm):
    """
    Custom AdminForm to enable messages to groups and all users.
    """
    recipient = ModelChoiceField(
        label=_('Recipient'), queryset=User.objects.all(), required=True)

    group = ChoiceField(label=_('group'), required=False,
        help_text=_('Creates the message optionally for all users or a group of users.'))

    def __init__(self, *args, **kwargs):
        super(MessageAdminForm, self).__init__(*args, **kwargs)
        self.fields['group'].choices = self._get_group_choices()

    def _get_group_choices(self):
        return [('', u'---------'), ('all', _('All users'))] +\
               [(group.pk, group.name) for group in Group.objects.all()]

    class Meta:
        model = Message

class MessageAdmin(admin.ModelAdmin):
    form = MessageAdminForm
    fieldsets = (
        (None, {
            'fields': (
                'sender',
                ('recipient', 'group'),
                ),
            }),
        (_('Message'), {
            'fields': (
                'parent_msg',
                'subject', 'body',
                ),
            'classes': ('monospace' ),
            }),
        (_('Date/time'), {
            'fields': (
                'sent_at', 'read_at', 'replied_at',
                'sender_deleted_at', 'recipient_deleted_at',
                'ip','user_agent',
                ),
            'classes': ('collapse', 'wide'),
            }),
        )
    list_display = ('__unicode__', 'sender', 'ip','recipient', 'sent_at', 'read_at')
    list_filter = ('sent_at', 'sender', 'recipient')
    search_fields = ('subject', 'body')

    def save_model(self, request, obj, form, change):
        """
        Saves the message for the recipient and looks in the form instance
        for other possible recipients. Prevents duplication by excludin the
        original recipient from the list of optional recipients.

        When changing an existing message and choosing optional recipients,
        the message is effectively resent to those users.
        """
        obj.save()

        if form.cleaned_data['group'] == 'all':
            # send to all users
            recipients = User.objects.exclude(pk=obj.recipient.pk)
        else:
            # send to a group of users
            recipients = []
            group = form.cleaned_data['group']
            if group:
                group = Group.objects.get(pk=group)
                recipients.extend(
                    list(group.user_set.exclude(pk=obj.recipient.pk)))
            # create messages for all found recipients
        for user in recipients:
            obj.pk = None
            obj.recipient = user
            obj.save()

admin.site.register(Message, MessageAdmin)
admin.site.register(Doc, DocAdmin)
admin.site.register(Pic, PicAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(VisitorHit, VisitorHitAdmin)
