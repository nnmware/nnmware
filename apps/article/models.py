from django.db import models
from django.utils.translation import ugettext_lazy as _
from nnmware.core.fields import RichTextField
from nnmware.core.models import Tree, MetaData


class Category(Tree):
    slug_detail = 'articles_category'

    class Meta:
        ordering = ['parent__id', 'title']
        verbose_name = _('ArticleCategory')
        verbose_name_plural = _('ArticleCategories')


class Article(MetaData):
    category = models.ForeignKey(Category, verbose_name=_('Category'), null=True, blank=True)
    content = RichTextField(_('Content'))

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")

    slug_detail = 'article_detail'
