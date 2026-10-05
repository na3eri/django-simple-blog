from apps.cms.models import Page
from django.db import models


class TestServiceModel(models.Model):
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=100, unique=True)
