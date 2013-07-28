from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import Region
from nnmware.apps.business.models import AbstractSeller
from nnmware.core.abstract import Tree, AbstractName, AbstractDate


class BoardCategory(Tree):
    slug_detail = 'board_category'

    class Meta:
        ordering = ['parent__id', 'title']
        verbose_name = _("BoardCategory")
        verbose_name_plural = _("BoardCategories")


class Board(AbstractName, AbstractDate, AbstractSeller):
    category = models.ForeignKey(BoardCategory, verbose_name=_("Category"), null=True, blank=True)
    region = models.ForeignKey(Region, verbose_name=_('Region'), blank=True, null=True, related_name="%(class)s_reg",
                               on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Board")
        verbose_name_plural = _("Boards")

    slug_detail = "board_detail"

    secured = models.BooleanField(verbose_name=_('Site-only contact'),
        default=False)

    def get_absolute_url(self):
        return "/board/%i/" % self.id

    def get_edit_url(self):
        return reverse("board_edit", self.id)

    def get_del_url(self):
        return reverse("board_del", self.id)

    def get_lock_url(self):
        return reverse("board_lock", self.id)

    def get_unlock_url(self):
        return reverse("board_unlock", self.id)

    def view_link(self):
        return '<a href="%s">%s</a>' % (self.get_absolute_url(), _('view'))

    view_link.allow_tags = True
