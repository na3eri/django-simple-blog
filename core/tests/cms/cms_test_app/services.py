from apps.cms.services.base_service import BaseService

from tests.cms.cms_test_app.forms import TestServiceModelForm
from tests.cms.cms_test_app.models import TestServiceModel


class TestService(BaseService):
    model = TestServiceModel
    form = TestServiceModelForm
    max_items = 3
    page_name = "test-service"
