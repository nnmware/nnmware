# nnmware(c)2012-2016

from django.db import models
from nnmware.core.abstract import Pic
from nnmware.core.models import NnmwareUser


class User(NnmwareUser):
    avatar = models.ForeignKey(Pic, blank=True, null=True, related_name="ava")
