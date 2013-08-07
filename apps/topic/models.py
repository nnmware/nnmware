from django.conf import settings
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import Region
from nnmware.core.abstract import Tree, AbstractDate, AbstractName, STATUS_CHOICES, STATUS_DRAFT
from nnmware.core.managers import TopicManager


class TopicCategory(Tree):
    slug_detail = 'topics_category'

    class Meta:
        ordering = ['parent__id', 'name']
        verbose_name = _('Topic Category')
        verbose_name_plural = _('Topic Categories')

    @property
    def _active_set(self):
        return Topic.objects.filter(category=self)


class Topic(AbstractDate, AbstractName):
    region = models.ForeignKey(Region, verbose_name=_('Region'), blank=True, null=True, related_name="%(class)s_reg",
                               on_delete=models.PROTECT)
    category = models.ForeignKey(TopicCategory, verbose_name=_('Category'), null=True, blank=True,
                                 on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), on_delete=models.PROTECT)
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, default=STATUS_DRAFT)

    objects = TopicManager()

    class Meta:
        ordering = ['-created_date', ]
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')

    @permalink
    def get_absolute_url(self):
        return "topic_detail", (), {'pk': self.pk}


    @permalink
    def get_edit_url(self):
        return 'topic_edit', (), {'pk': self.pk}
