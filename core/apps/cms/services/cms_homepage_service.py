from apps.cms.forms import (
    HomePageCategoryForm,
    HomePageSliderForm,
)
from apps.cms.models import (
    HomePageCategory,
    HomePageSlider,
)
from apps.cms.services.base_service import BaseService


class SlidersService(BaseService):
    model = HomePageSlider
    form = HomePageSliderForm
    max_items = 4
    page_name = "home"


class CategoryService(BaseService):
    model = HomePageCategory
    form = HomePageCategoryForm
    max_items = 3
    page_name = "home"


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
            "status": result["status"],
            "form": result["form"],
            "detail": (
                "Form was processed successfully"
                if result["status"]
                else "Form processing failed"
            ),
        }
