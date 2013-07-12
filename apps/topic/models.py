from datetime import datetime
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from nnmware.core.abstract import Tree, AbstractData





class Category(Tree):
    slug_detail = 'topic_category'

    class Meta:
        ordering = ['parent__id', 'title']
        verbose_name = _("TopicCategory")
        verbose_name_plural = _("TopicCategories")


class Topic(AbstractData):
    category = models.ForeignKey(Category, verbose_name=_("Category"),
        null=True, blank=True, related_name="topic_category")

    class Meta:
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")

    def get_absolute_url(self):
        return reverse("topic_one", self.id)

    def get_edit_url(self):
        return reverse("topic_edit", self.id)


