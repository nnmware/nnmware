# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.db.models import permalink, Count
from django.utils.translation import ugettext_lazy as _
from nnmware.core.models import Like
from nnmware.apps.address.models import Region
from nnmware.core.abstract import Tree, AbstractDate, AbstractName, STATUS_CHOICES, STATUS_DRAFT
from nnmware.core.managers import PublicationManager


class PublicationCategory(Tree):
    slug_detail = 'publication_category'

    class Meta:
        ordering = ['parent__id', 'name']
        verbose_name = _('Publication Category')
        verbose_name_plural = _('Publication Categories')

    @property
    def _active_set(self):
        return Publication.objects.filter(category=self)


class Publication(AbstractDate, AbstractName):
    region = models.ForeignKey(Region, verbose_name=_('Region'), blank=True, null=True, related_name="%(class)s_reg",
                               on_delete=models.PROTECT)
    category = models.ForeignKey(PublicationCategory, verbose_name=_('Category'), null=True, blank=True,
                                 on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), on_delete=models.PROTECT)
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, default=STATUS_DRAFT)

    objects = PublicationManager()

    class Meta:
        ordering = ['-created_date', ]
        verbose_name = _('Publication')
        verbose_name_plural = _('Publications')

    @permalink
    def get_absolute_url(self):
        return "publication_detail", (), {'pk': self.pk}

    @permalink
    def get_edit_url(self):
        return 'publication_edit', (), {'pk': self.pk}

    def carma(self):
        liked = Like.objects.for_object(self).filter(like=True).aggregate(Count("id"))['id__count']
        disliked = Like.objects.for_object(self).filter(dislike=True).aggregate(Count("id"))['id__count']
        return liked - disliked

    # def users_liked(self):
    #     return self.liked().values_list('user__pk', flat=True)
    #
    # def users_disliked(self):
    #     return self.disliked().values_list('user__pk', flat=True)
