# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models

class MetaDate(models.Model):
    created_date = models.DateTimeField(_("Created date"), default=datetime.now())
    updated_date = models.DateTimeField(_("Updated date"), null=True, blank=True)

    class Meta:
        abstract = True
