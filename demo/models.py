
from django.db import models
from nnmware.core.models import Pic, NnmwareUser

class User(NnmwareUser):
    avatar = models.ForeignKey(Pic, blank=True, null=True, related_name="ava")
