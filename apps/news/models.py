from django.conf import settings
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import Region
from nnmware.core.abstract import Tree, AbstractDate, AbstractName, AbstractTeaser
from nnmware.core.constants import STATUS_CHOICES, STATUS_DRAFT
from nnmware.core.managers import NewsManager


class NewsCategory(Tree):
    slug_detail = 'news_category'

    class Meta:
        ordering = ['parent__id', 'name']
        verbose_name = _('News Category')
        verbose_name_plural = _('News Categories')

    @property
    def obj_active_set(self):
        return News.objects.filter(category=self)


class News(AbstractDate, AbstractName, AbstractTeaser):
    region = models.ForeignKey(Region, verbose_name=_('Region'), blank=True, null=True, related_name="%(class)s_reg",
                               on_delete=models.PROTECT)
    category = models.ForeignKey(NewsCategory, verbose_name=_('Category'), null=True, blank=True,
                                 on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), on_delete=models.PROTECT)
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, default=STATUS_DRAFT)

    objects = NewsManager()

    class Meta:
        ordering = ['-created_date', ]
        verbose_name = _('News')
        verbose_name_plural = _('Many news')

    @permalink
    def get_absolute_url(self):
        return "news_detail", (), {'pk': self.pk}

    @permalink
    def get_edit_url(self):
        return 'news_edit', (), {'pk': self.pk}
