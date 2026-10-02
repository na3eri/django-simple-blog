from apps.cms.forms import (
    HomePageCategoryForm,
    HomePageSliderForm,
)
from apps.cms.models import (
    HomePageCategory,
    HomePageSlider,
    Page,
)
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404


class BaseService:
    model = None
    form = None
    max_items = None

    def __init__(self):

        try:
            self.page = Page.objects.get(name="home")

        except Page.DoesNotExist:
            self.page = Page.objects.create(name="home")

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
            return False

        if pk is None and not self.can_add():
            return False

        form = self.build_form(
            post_data=post_data,
            files_data=files_data,
            instance=instance,
        )

        if not form.is_valid():
            return False

        instance = form.save(commit=False)
        instance.page = self.page

        try:
            with transaction.atomic():
                instance.save()

        except IntegrityError:
            return False

        return True

    def delete(self, pk):

        instance = get_object_or_404(
            self.model,
            pk=pk,
            page=self.page,
        )

        instance.delete()


class SlidersService(BaseService):
    model = HomePageSlider
    form = HomePageSliderForm
    max_items = 4


class CategoryService(BaseService):
    model = HomePageCategory
    form = HomePageCategoryForm
    max_items = 3


class CMSHomePageService:
    def __init__(self):

        self.slider_service = SlidersService()
        self.category_service = CategoryService()

    def build_sliders(self):

        return self.slider_service.get_all()

    def build_categories(self):

        return self.category_service.get_all()

    def build_slider_form(
        self,
        post_data=None,
        files_data=None,
        instance: HomePageSlider | None = None,
    ):

        return self.slider_service.build_form(
            post_data=post_data,
            files_data=files_data,
            instance=instance,
        )

    def build_category_form(
        self,
        post_data=None,
        files_data=None,
        instance: HomePageCategory | None = None,
    ):

        return self.category_service.build_form(
            post_data=post_data,
            files_data=files_data,
            instance=instance,
        )

    def delete_slider(self, pk):

        self.slider_service.delete(pk=pk)

    def delete_category(self, pk):

        self.category_service.delete(pk=pk)

    def handle_form(
        self,
        form_type,
        post_data,
        files_data=None,
        pk=None,
    ):

        services = {
            "slider_form": self.slider_service,
            "category_form": self.category_service,
        }

        service = services.get(form_type)

        if service is None:
            return None

        result = service.handle_form(
            post_data=post_data,
            files_data=files_data,
            pk=pk,
        )

        return {
            "status": result,
            "detail": (
                "Form was processed successfully"
                if result
                else "Form processing failed"
            ),
        }
