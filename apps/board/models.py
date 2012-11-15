from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from nnmware.core.abstract import Tree, AbstractData


class Category(Tree):
    slug_detail = 'board_category'

    class Meta:
        ordering = ['parent__id', 'title']
        verbose_name = _("BoardCategory")
        verbose_name_plural = _("BoardCategories")


class Board(AbstractData):
    category = models.ForeignKey(Category, verbose_name=_("Category"),
        null=True, blank=True)

    class Meta:
        verbose_name = _("Board")
        verbose_name_plural = _("Boards")

    slug_detail = "board_detail"

    email = models.EmailField(_(u'Email'), blank=True)
    icq = models.DecimalField(_(u'ICQ'), max_digits=20, decimal_places=0,
        null=True, blank=True)
    phone = models.DecimalField(_(u'Phone'), max_digits=20,
        decimal_places=0, null=True, blank=True)
    contact = models.CharField(_(u'Contact'), max_length=150,
        null=True, blank=True)
    secured = models.BooleanField(verbose_name=_(u'Site-only contact'),
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
        return u'<a href="%s">%s</a>' % (self.get_absolute_url(), _('view'))

    view_link.allow_tags = True
