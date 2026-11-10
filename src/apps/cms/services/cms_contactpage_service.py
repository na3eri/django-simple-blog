from apps.cms.forms import ContactPageDataForm
from apps.cms.models import ContactPageData
from apps.cms.services.base_service import BaseService


class ContactService(BaseService):
    model = ContactPageData
    form = ContactPageDataForm
    max_items = 1
    page_name = "contact"

    @property
    def contact_instance(self):

        return self.get_all().first()

    def handle_form(
        self,
        post_data,
        files_data=None,
    ):

        instance = self.contact_instance

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


class CMSContactPageService:
    def __init__(self):

        self.contact_service = ContactService()

    def build_form(
        self,
        post_data=None,
        files_data=None,
        instance=None,
    ):

        return self.contact_service.build_form(
            post_data=post_data,
            files_data=files_data,
            instance=instance,
        )

    @property
    def contact_data_instance(self):

        return self.contact_service.contact_instance

    def handle_form(
        self,
        post_data,
        files_data=None,
    ):

        result = self.contact_service.handle_form(
            post_data=post_data,
            files_data=files_data,
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
