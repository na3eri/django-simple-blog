from apps.cms.models import ContactPageData


class ContactPageService:
    def __init__(self):
        self.contact_data = ContactPageData

    def build_data(self):
        return ContactPageData.objects.first()
