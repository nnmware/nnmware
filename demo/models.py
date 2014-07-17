# -*- coding: utf-8 -*-

from django.db import models
from core.abstract import Pic
from nnmware.core.models import NnmwareUser


class User(NnmwareUser):
    avatar = models.ForeignKey(Pic, blank=True, null=True, related_name="ava")
