# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from nnmware.core.abstract import Pic, Doc
from nnmware.core.models import Nnmcomment, Tag, Action, Follow, Notice, Message, VisitorHit, Video, \
    EmailValidation, FlatNnmcomment, Like, ContentBlock


class TypeBaseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


class BaseSkillInline(admin.StackedInline):
    fields = (('skill', 'level', 'addon'),)


@admin.register(FlatNnmcomment)
class FlatNnmcommentAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Comment'), {'fields': [('content_type', 'object_id', 'status')]}),
        (_('Content'), {'fields': [('user', 'comment')]}),
        (_('Meta'), {'fields': [('created_date', 'updated_date',
                                 'ip')]}),
    )
    list_display = ('user', 'created_date', 'content_type', 'status', 'comment')
    list_filter = ('created_date',)
    date_hierarchy = 'created_date'
    search_fields = ('comment', 'user__username')


@admin.register(Nnmcomment)
class NnmcommentAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Comment'), {'fields': [('parent', 'content_type', 'object_id')]}),
        (_('Content'), {'fields': [('comment', 'user', 'status')]}),
        (_('Meta'), {'fields': [('created_date', 'updated_date',
                                 'ip')]}),
    )
    list_display = ('user', 'created_date', 'content_type',
                    'parent', '__str__', 'status')
    list_filter = ('created_date',)
    date_hierarchy = 'created_date'
    search_fields = ('comment', 'user__username')


class TreeAdmin(admin.ModelAdmin):
    list_display = ('name', '_parents_repr', 'enabled', 'rootnode', 'position')
    list_display_links = ("name",)
    list_filter = ("name",)
    ordering = ['parent__id', 'name']
    prepopulated_fields = {'slug': ('name',)}
    actions = None
    search_fields = ("name", )
    fieldsets = (
        (_("Main"), {"fields": [("name", "slug"), ("parent",
                                                   "login_required",)]}),
        (_("Description"), {"classes": ("collapse",),
                            "fields": [("description",), ("position", "rootnode"), ]}),
    )


@admin.register(Doc)
class DocAdmin(admin.ModelAdmin):
    """
     Admin class for Doc.
     """
    #    readonly_fields = ('file',)
    fieldsets = (
        (_('nnmware'), {'fields': [('user', 'content_type', 'object_id')]}),
        (_('Doc'), {'fields': [('doc', 'created_date', 'position')]}),
        (_('Meta'), {'fields': [('description', 'filetype')]}),
    )
    list_display = ('description', 'doc', 'created_date', 'user', 'locked', 'size')


@admin.register(Pic)
class PicAdmin(admin.ModelAdmin):
    # readonly_fields = ('pic',)
    fieldsets = (
        (_('nnmware'), {'fields': [('user', 'content_type', 'object_id')]}),
        (_('Pic'), {'fields': [('pic', 'created_date')]}),
        (_('Meta'), {'fields': [('description', 'source')]}),
    )
    list_display = ('user', 'created_date', 'content_type',
                    'slide_thumbnail', '__str__')
    list_filter = ('created_date',)
    date_hierarchy = 'created_date'
    search_fields = ('description', 'user__username')


@admin.register(VisitorHit)
class VisitorHitAdmin(admin.ModelAdmin):
    readonly_fields = ('user', 'date', 'ip', 'session_key', 'user_agent', 'referer',
                       'url', 'secure', 'hostname')
    fieldsets = ((_('Visitor hit'), {'fields': [('user', 'date', 'secure'), ('ip', 'session_key'),
                                                ('user_agent', 'referer'), ('url', 'hostname'), ]}),)
    list_display = ('user', 'date', 'ip', 'user_agent', 'url', 'secure', 'referer')
    list_filter = ('date', 'user', 'ip')
    search_fields = ('user__username', 'user_agent', 'ip', 'url')
    ordering = ('-date', 'user', 'ip')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fieldsets = ((_('nnmware'), {'fields': [('name', 'slug')]}),)
    list_display = ('name', 'slug')


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('user', 'verb', 'timestamp', 'ip', 'user_agent')
    list_filter = ('timestamp',)


class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_filter = ('name',)


class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'thumbnail')
    list_filter = ('name',)


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'slide_thumbnail')
    list_filter = ('name',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user')
    list_editable = ('user',)
    list_filter = ('user',)


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'verb', 'sender', 'ip', 'user_agent')
    list_filter = ('user',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Main'), {
            'fields': (
                'sender',
                ('recipient', ),
            ),
        }),
        (_("Message"), {"classes": ("collapse",), "fields": [('subject',), ('body',), ('parent_msg',)]}),
        (_("Date/Time"), {"classes": ("collapse",), "fields": [('sent_at', 'read_at', 'replied_at'),
                                                               ('sender_deleted_at', 'recipient_deleted_at'),
                                                               ('ip', 'user_agent')]}),
    )
    list_display = ('pk', 'sender', 'ip', 'recipient', 'sent_at', 'read_at')
    list_filter = ('sent_at', 'sender', 'recipient')
    search_fields = ('subject', 'body')


@admin.register(EmailValidation)
class EmailValidationAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = ('username', 'email')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'user', 'slug', 'description')
    list_filter = ('user', 'project_name')
    search_fields = ('user__username', 'user__first_name')
    filter_horizontal = ['tags', 'users_viewed']
    fieldsets = (
        (_("Main"), {"fields": [("user", "project_name"),
                                ('project_url', 'video_url')]}),
        (_("Addons"), {"fields": [('description',), ('login_required', 'slug'),
                                  ('img',)]}),
        (_("Tags"), {"classes": ("collapse",), "fields": [
            ('tags',)]}),
        (_("Users viewed"), {"classes": ("collapse",), "fields": [
            ('users_viewed',)]}),
    )


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Like'), {'fields': [('user', 'content_type', 'object_id')]}),
        (_('Variants'), {'fields': [('status',)]}),
    )
    list_display = ('user', 'status')
    readonly_fields = ('user', 'content_type', 'object_id', 'status')


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Content block'), {'fields': [('user', 'content_type', 'object_id'), ('status', 'content_style', 'position'),
                                         ('description',)]}),
        (_('Origin'), {'fields': [('url', 'author', 'teaser')]}),
    )
    list_display = ('user', 'status', 'content_style', 'teaser')
    readonly_fields = ('user', 'content_type', 'object_id')
