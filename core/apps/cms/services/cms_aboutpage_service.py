from apps.cms.forms import AboutPageDataForm, AboutPageImageForm
from apps.cms.models import AboutPageData, AboutPageImage
from apps.cms.services.base_service import BaseService


class AboutDataService(BaseService):
    model = AboutPageData
    form = AboutPageDataForm
    max_items = 1
    page_name = "about"

    @property
    def about_instance(self):
        return self.get_all().first()

    def handle_form(
        self,
        post_data,
        files_data=None,
        pk=None,
    ):
        instance = self.about_instance

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
        instance.save()

        return {
            "status": True,
            "form": form,
        }


class AboutImageService(BaseService):
    model = AboutPageImage
    form = AboutPageImageForm
    max_items = 3
    page_name = "about"


class CMSAboutPageService:
    def __init__(self):
        self.about_data_service = AboutDataService()
        self.about_image_service = AboutImageService()

    def build_form(
        self,
        form_type,
        post_data=None,
        files_data=None,
        instance=None,
    ):
        services = {
            "about_data": self.about_data_service,
            "about_image": self.about_image_service,
        }

        service = services.get(form_type)

        if not service:
            return None

        return service.build_form(
            post_data=post_data,
            files_data=files_data,
            instance=instance,
        )

    def build_images(self):
        return self.about_image_service.get_all()

    @property
    def about_data_instance(self):
        return self.about_data_service.about_instance

    def handle_form(
        self,
        form_type,
        post_data,
        files_data=None,
        pk=None,
    ):
        services = {
            "about_data": self.about_data_service,
            "about_image": self.about_image_service,
        }

        service = services.get(form_type)

        result = service.handle_form(post_data=post_data, files_data=files_data, pk=pk)

        return {
            "status": result["status"],
            "form": result["form"],
            "detail": (
                "Form was processed successfully"
                if result["status"]
                else "Form processing failed"
            ),
        }
