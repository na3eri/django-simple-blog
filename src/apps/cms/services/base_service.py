from apps.cms.models import Page
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404


class BaseService:
    model = None
    form = None
    max_items = None
    page_name = None

    def __init__(self):

        if self.page_name is None:
            raise ValueError("page_name must be defined.")

        self.page, _ = Page.objects.get_or_create(name=self.page_name)

    def get_all(self):

        return self.model.objects.filter(page=self.page)

    def get_one(self, pk):

        try:
            return self.model.objects.get(
                pk=pk,
                page=self.page,
            )

        except self.model.DoesNotExist:
            return None

    def build_form(
        self,
        post_data=None,
        files_data=None,
        instance=None,
    ):

        return self.form(
            data=post_data,
            files=files_data,
            instance=instance,
        )

    def can_add(self):

        if self.max_items is None:
            return True

        return self.get_all().count() < self.max_items

    def handle_form(
        self,
        post_data,
        files_data=None,
        pk=None,
    ):

        instance = self.get_one(pk) if pk is not None else None

        if pk is not None and instance is None:
            return {
                "status": False,
                "form": None,
            }

        if pk is None and not self.can_add():
            return {
                "status": False,
                "form": None,
            }

        form = self.build_form(
            post_data=post_data,
            files_data=files_data,
            instance=instance,
        )

        if not form.is_valid():
            return {
                "status": False,
                "form": form,
            }

        instance = form.save(commit=False)
        instance.page = self.page

        try:
            with transaction.atomic():
                instance.save()

        except IntegrityError:
            return {
                "status": False,
                "form": form,
            }

        return {
            "status": True,
            "form": form,
        }

    def delete(self, pk):

        instance = get_object_or_404(
            self.model,
            pk=pk,
            page=self.page,
        )

        instance.delete()
