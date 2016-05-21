# nnmware(c)2012-2016

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.address.models import Region
from nnmware.apps.business.models import AbstractSeller
from nnmware.core.abstract import Tree, AbstractName, AbstractDate


class BoardCategory(Tree):
    slug_detail = 'board_category'

    class Meta:
        ordering = ['parent__id', 'name']
        verbose_name = _("BoardCategory")
        verbose_name_plural = _("BoardCategories")

    @property
    def obj_active_set(self):
        return Board.objects.filter(category=self)


class Board(AbstractName, AbstractDate, AbstractSeller):
    category = models.ForeignKey(BoardCategory, verbose_name=_("Category"), null=True, blank=True)
    region = models.ForeignKey(Region, verbose_name=_('Region'), blank=True, null=True, related_name="%(class)s_reg",
                               on_delete=models.PROTECT)
    secured = models.BooleanField(verbose_name=_('Site-only contact'), default=False)

    class Meta:
        verbose_name = _("Board")
        verbose_name_plural = _("Boards")

    slug_detail = "board_detail"

    def get_absolute_url(self):
        return reverse("board_detail", args=[self.id])

    def get_edit_url(self):
        return reverse("board_edit", args=[self.id])

    def get_del_url(self):
        return reverse("board_del", args=[self.id])

    def get_lock_url(self):
        return reverse("board_lock", args=[self.id])

    def get_unlock_url(self):
        return reverse("board_unlock", args=[self.id])

    def view_link(self):
        return '<a href="%s">%s</a>' % (self.get_absolute_url(), _('view'))

    view_link.allow_tags = True
