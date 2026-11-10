from django.db import models

from apps.cms.models import Page


class TestServiceModel(models.Model):
    __test__ = False

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=100, unique=True)
