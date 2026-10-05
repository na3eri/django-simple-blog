import factory
import pytest
from apps.cms.forms import (
    AboutPageDataForm,
    AboutPageImageForm,
    ContactPageDataForm,
    HomePageCategoryForm,
    HomePageSliderForm,
)
from apps.cms.models import (
    AboutPageData,
    AboutPageImage,
    ContactPageData,
    HomePageCategory,
    HomePageSlider,
)
from apps.cms.services.base_service import BaseService
from apps.cms.services.cms_aboutpage_service import (
    AboutDataService,
    AboutImageService,
    CMSAboutPageService,
)
from apps.cms.services.cms_contactpage_service import (
    CMSContactPageService,
    ContactService,
)
from apps.cms.services.cms_homepage_service import (
    CategoryService,
    CMSHomePageService,
    SlidersService,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.http import Http404

from tests.cms.cms_test_app.forms import TestServiceModelForm
from tests.cms.cms_test_app.models import TestServiceModel
from tests.cms.cms_test_app.services import TestService

pytestmark = pytest.mark.django_db


class TestBaseService:
    def test_init_object_variables(self):
        service = TestService()
        assert service.page.name == "test-service"

    def test_init_without_page_name(self):
        with pytest.raises(
            ValueError,
            match="page_name must be defined.",
        ):
            BaseService()

    def test_get_all_method(self, test_service_model_factory):
        service = TestService()
        test_service_model_factory.create_batch(
            10,
            page=service.page,
            title=factory.Faker("sentence", nb_words=6),
        )
        assert set(service.get_all()) == set(
            TestServiceModel.objects.filter(page__name=service.page.name)
        )

    def test_get_one_method(self, test_service_model_factory):
        service = TestService()
        test_instance = test_service_model_factory(
            page=service.page,
            title="some title",
        )
        assert service.get_one(pk=test_instance.id) == TestServiceModel.objects.get(
            pk=test_instance.id
        )
        assert service.get_one(pk=999) is None

    def test_build_form_method(self):
        service = TestService()
        form = service.build_form()
        assert isinstance(form, TestServiceModelForm)

    def test_can_add_method(self, test_service_model_factory):
        class Test(BaseService):
            model = TestServiceModel
            form = TestServiceModelForm
            page_name = "something"
            max_items = None

        service = Test()
        assert service.can_add() is True

        service = TestService()
        test_service_model_factory.create_batch(
            3,
            page=service.page,
            title=factory.Faker("sentence", nb_words=6),
        )
        assert service.can_add() is False

    def test_handle_form_invalid_pk(self):
        service = TestService()
        result = service.handle_form(
            post_data={"title": "test wrong"},
            pk=999,
        )
        assert result == {
            "status": False,
            "form": None,
        }

    def test_handle_form_update(self, test_service_model_factory):
        service = TestService()
        test_instance = test_service_model_factory(
            page=service.page,
            title="test title for example",
        )
        result = service.handle_form(
            post_data={"title": "test example post data"},
            pk=test_instance.id,
        )
        assert result["status"] is True
        assert isinstance(result["form"], TestServiceModelForm)

    def test_handle_form_invalid_form(self):
        service = TestService()
        result = service.handle_form(
            post_data={"invalid_field": "invalid_data"},
        )
        assert result["status"] is False
        assert isinstance(result["form"], TestServiceModelForm)

    def test_handle_form_max_items(self, test_service_model_factory):
        service = TestService()
        test_service_model_factory.create_batch(
            3,
            page=service.page,
            title=factory.Faker("sentence", nb_words=6),
        )
        result = service.handle_form(
            post_data={"title": "last attempt to test can add method"},
        )
        assert result == {
            "status": False,
            "form": None,
        }

    def test_handle_form_integrity_error(self, monkeypatch):
        service = TestService()

        def raise_integrity_error(*args, **kwargs):
            raise IntegrityError

        monkeypatch.setattr(
            TestServiceModel,
            "save",
            raise_integrity_error,
        )

        result = service.handle_form(
            post_data={"title": "test title"},
        )
        assert result["status"] is False
        assert isinstance(result["form"], TestServiceModelForm)

    def test_delete_method_for_exist(self, test_service_model_factory):
        service = TestService()
        instance = test_service_model_factory(
            page=service.page,
            title="test delete method",
        )
        instance_pk = instance.id

        service.delete(instance_pk)

        assert service.get_one(instance_pk) == None

    def test_delete_method_for_not_exist(self):
        service = TestService()

        with pytest.raises(Http404):
            service.delete(999)


class TestAboutDataService:
    def test_about_instance_without_data(self):
        service = AboutDataService()
        assert service.about_instance is None

    def test_about_instance_with_data(self, about_page_data_factory):
        service = AboutDataService()
        instance = about_page_data_factory(
            page=service.page,
        )
        assert service.about_instance == instance

    def test_handle_form_invalid(self):
        service = AboutDataService()
        result = service.handle_form(
            post_data={},
        )
        assert result["status"] is False
        assert isinstance(result["form"], AboutPageDataForm)

    def test_handle_form_success(self):
        service = AboutDataService()
        result = service.handle_form(
            post_data={
                "title": "About title",
                "subtitle": "About subtitle",
                "first_description": "First description",
                "second_description": "Second description",
                "third_description": "Third description",
            },
        )
        assert result["status"] is True
        assert isinstance(result["form"], AboutPageDataForm)
        assert AboutPageData.objects.filter(
            page=service.page,
        ).exists()

    def test_handle_form_updates_existing_instance(
        self,
        about_page_data_factory,
    ):
        service = AboutDataService()
        instance = about_page_data_factory(
            page=service.page,
        )
        result = service.handle_form(
            post_data={
                "title": "Updated title",
                "subtitle": "Updated subtitle",
                "first_description": "Updated first description",
                "second_description": "Updated second description",
                "third_description": "Updated third description",
            },
        )
        assert result["status"] is True
        instance.refresh_from_db()
        assert instance.title == "Updated title"


class TestAboutImageService:
    def test_service_configuration(self):
        service = AboutImageService()
        assert service.model is AboutPageImage
        assert service.form is AboutPageImageForm
        assert service.max_items == 3
        assert service.page_name == "about"


class TestCMSAboutPageService:
    def test_init(self):
        service = CMSAboutPageService()
        assert isinstance(service.about_data_service, AboutDataService)
        assert isinstance(service.about_image_service, AboutImageService)

    def test_build_form_about_data(self):
        service = CMSAboutPageService()
        form = service.build_form(
            form_type="about_data",
        )
        assert isinstance(form, AboutPageDataForm)

    def test_build_form_about_image(self):
        service = CMSAboutPageService()
        form = service.build_form(
            form_type="about_image",
        )
        assert isinstance(form, AboutPageImageForm)

    def test_build_form_invalid_type(self):
        service = CMSAboutPageService()
        assert (
            service.build_form(
                form_type="invalid",
            )
            is None
        )

    def test_build_images_empty(self):
        service = CMSAboutPageService()
        assert list(service.build_images()) == []

    def test_build_images(self, about_page_image_factory):
        service = CMSAboutPageService()
        about_page_image_factory(
            page=service.about_image_service.page,
        )
        assert list(service.build_images()) == list(
            AboutPageImage.objects.filter(
                page=service.about_image_service.page,
            )
        )

    def test_about_data_instance_without_data(self):
        service = CMSAboutPageService()
        assert service.about_data_instance is None

    def test_about_data_instance_with_data(self, about_page_data_factory):
        service = CMSAboutPageService()
        instance = about_page_data_factory(
            page=service.about_data_service.page,
        )
        assert service.about_data_instance == instance

    def test_handle_form_about_data_success(self):
        service = CMSAboutPageService()
        result = service.handle_form(
            form_type="about_data",
            post_data={
                "title": "About title",
                "subtitle": "About subtitle",
                "first_description": "First description",
                "second_description": "Second description",
                "third_description": "Third description",
            },
        )
        assert result == {
            "status": True,
            "form": result["form"],
            "detail": "Form was processed successfully",
        }

    def test_handle_form_about_data_failed(self):
        service = CMSAboutPageService()
        result = service.handle_form(
            form_type="about_data",
            post_data={},
        )
        assert result["status"] is False
        assert isinstance(result["form"], AboutPageDataForm)
        assert result["detail"] == "Form processing failed"

    def test_handle_form_about_image_success(self, about_page_image_factory):
        service = CMSAboutPageService()
        image = about_page_image_factory.build().image
        result = service.handle_form(
            form_type="about_image",
            post_data={
                "alt_message": "test",
            },
            files_data={
                "image": image,
            },
        )
        assert result["status"] is True
        assert isinstance(result["form"], AboutPageImageForm)
        assert result["detail"] == "Form was processed successfully"


class TestContactService:
    def test_contact_instance_without_data(self):
        service = ContactService()
        assert service.contact_instance is None

    def test_contact_instance_with_data(self, contact_page_data_factory):
        service = ContactService()
        instance = contact_page_data_factory(
            page=service.page,
        )
        assert service.contact_instance == instance

    def test_handle_form_invalid(self):
        service = ContactService()
        result = service.handle_form(
            post_data={},
        )
        assert result["status"] is False
        assert isinstance(result["form"], ContactPageDataForm)

    def test_handle_form_success(self):
        service = ContactService()
        result = service.handle_form(
            post_data={
                "address": "Test address",
                "email": "test@example.com",
                "phone_number": "+999999999",
                "linkedin_url": "https://linkedin.com/in/test",
                "instagram_url": "https://instagram.com/test",
                "x_url": "https://x.com/test",
                "facebook_url": "https://facebook.com/test",
                "map_url": "https://maps.google.com/test",
            },
        )
        assert result["status"] is True
        assert isinstance(result["form"], ContactPageDataForm)
        assert ContactPageData.objects.filter(
            page=service.page,
        ).exists()

    def test_handle_form_updates_existing_instance(
        self,
        contact_page_data_factory,
    ):
        service = ContactService()
        instance = contact_page_data_factory(
            page=service.page,
        )
        result = service.handle_form(
            post_data={
                "address": "Updated address",
                "email": "updated@example.com",
                "phone_number": "+111111111",
                "linkedin_url": "https://linkedin.com/in/updated",
                "instagram_url": "https://instagram.com/updated",
                "x_url": "https://x.com/updated",
                "facebook_url": "https://facebook.com/updated",
                "map_url": "https://maps.google.com/updated",
            },
        )
        assert result["status"] is True
        instance.refresh_from_db()
        assert instance.address == "Updated address"


class TestCMSContactPageService:
    def test_init(self):
        service = CMSContactPageService()
        assert isinstance(service.contact_service, ContactService)

    def test_build_form(self):
        service = CMSContactPageService()
        form = service.build_form()
        assert isinstance(form, ContactPageDataForm)

    def test_contact_data_instance_without_data(self):
        service = CMSContactPageService()
        assert service.contact_data_instance is None

    def test_contact_data_instance_with_data(
        self,
        contact_page_data_factory,
    ):
        service = CMSContactPageService()
        instance = contact_page_data_factory(
            page=service.contact_service.page,
        )
        assert service.contact_data_instance == instance

    def test_handle_form_success(self):
        service = CMSContactPageService()
        result = service.handle_form(
            post_data={
                "address": "Test address",
                "email": "test@example.com",
                "phone_number": "+999999999",
                "linkedin_url": "https://linkedin.com/in/test",
                "instagram_url": "https://instagram.com/test",
                "x_url": "https://x.com/test",
                "facebook_url": "https://facebook.com/test",
                "map_url": "https://maps.google.com/test",
            },
        )
        assert result["status"] is True
        assert isinstance(result["form"], ContactPageDataForm)
        assert result["detail"] == "Form was processed successfully"

    def test_handle_form_failed(self):
        service = CMSContactPageService()
        result = service.handle_form(
            post_data={},
        )
        assert result["status"] is False
        assert isinstance(result["form"], ContactPageDataForm)
        assert result["detail"] == "Form processing failed"


class TestSlidersService:
    def test_service_configuration(self):
        service = SlidersService()
        assert service.model is HomePageSlider
        assert service.form is HomePageSliderForm
        assert service.max_items == 4
        assert service.page_name == "home"

    def test_get_all(self, home_page_slider_factory):
        service = SlidersService()
        instance = home_page_slider_factory(
            page=service.page,
        )
        assert list(service.get_all()) == [instance]

    def test_build_form(self):
        service = SlidersService()
        form = service.build_form()
        assert isinstance(form, HomePageSliderForm)

    def test_can_add_when_empty(self):
        service = SlidersService()
        assert service.can_add() is True

    def test_can_add_when_limit_reached(
        self,
        home_page_category_factory,
        category_factory,
    ):
        service = CategoryService()
        for order in range(1, 4):
            category = category_factory(
                name=f"test-{order}",
            )
            home_page_category_factory(
                page=service.page,
                category=category,
                order=order,
            )
        assert service.can_add() is False


class TestCategoryService:
    def test_service_configuration(self):
        service = CategoryService()
        assert service.model is HomePageCategory
        assert service.form is HomePageCategoryForm
        assert service.max_items == 3
        assert service.page_name == "home"

    def test_get_all(self, home_page_category_factory):
        service = CategoryService()
        instance = home_page_category_factory(
            page=service.page,
        )
        assert list(service.get_all()) == [instance]

    def test_build_form(self):
        service = CategoryService()
        form = service.build_form()
        assert isinstance(form, HomePageCategoryForm)

    def test_can_add_when_empty(self):
        service = CategoryService()
        assert service.can_add() is True

    def test_can_add_when_limit_reached(
        self,
        home_page_category_factory,
        category_factory,
    ):
        service = CategoryService()
        for order in range(1, 4):
            category = category_factory(
                name=f"test-{order}",
            )
            home_page_category_factory(
                page=service.page,
                category=category,
                order=order,
            )
        assert service.can_add() is False


class TestCMSHomePageService:
    def test_init(self):
        service = CMSHomePageService()
        assert isinstance(service.slider_service, SlidersService)
        assert isinstance(service.category_service, CategoryService)

    def test_build_sliders_empty(self):
        service = CMSHomePageService()
        assert list(service.build_sliders()) == []

    def test_build_sliders(self, home_page_slider_factory):
        service = CMSHomePageService()
        instance = home_page_slider_factory(
            page=service.slider_service.page,
        )
        assert list(service.build_sliders()) == [instance]

    def test_build_categories_empty(self):
        service = CMSHomePageService()
        assert list(service.build_categories()) == []

    def test_build_categories(self, home_page_category_factory):
        service = CMSHomePageService()
        instance = home_page_category_factory(
            page=service.category_service.page,
        )
        assert list(service.build_categories()) == [instance]

    def test_build_slider_form(self):
        service = CMSHomePageService()
        form = service.build_slider_form()
        assert isinstance(form, HomePageSliderForm)

    def test_build_category_form(self):
        service = CMSHomePageService()
        form = service.build_category_form()
        assert isinstance(form, HomePageCategoryForm)

    def test_build_slider_form_with_instance(
        self,
        home_page_slider_factory,
    ):
        service = CMSHomePageService()
        instance = home_page_slider_factory(
            page=service.slider_service.page,
        )
        form = service.build_slider_form(
            instance=instance,
        )
        assert form.instance == instance

    def test_build_category_form_with_instance(
        self,
        home_page_category_factory,
    ):
        service = CMSHomePageService()
        instance = home_page_category_factory(
            page=service.category_service.page,
        )
        form = service.build_category_form(
            instance=instance,
        )
        assert form.instance == instance

    def test_delete_slider(
        self,
        home_page_slider_factory,
    ):
        service = CMSHomePageService()
        instance = home_page_slider_factory(
            page=service.slider_service.page,
        )
        service.delete_slider(pk=instance.pk)
        assert not HomePageSlider.objects.filter(
            pk=instance.pk,
        ).exists()

    def test_delete_category(
        self,
        home_page_category_factory,
    ):
        service = CMSHomePageService()
        instance = home_page_category_factory(
            page=service.category_service.page,
        )
        service.delete_category(pk=instance.pk)
        assert not HomePageCategory.objects.filter(
            pk=instance.pk,
        ).exists()

    def test_handle_slider_form_success(
        self,
        home_page_slider_factory,
    ):
        service = CMSHomePageService()
        image = home_page_slider_factory.build().image
        result = service.handle_form(
            form_type="slider_form",
            post_data={
                "title": "Test title",
                "subtitle": "Test subtitle",
                "alt_message": "Test alt message",
                "url": "https://example.com/test",
                "order": 1,
            },
            files_data={
                "image": image,
            },
        )
        assert result["status"] is True
        assert isinstance(result["form"], HomePageSliderForm)
        assert result["detail"] == "Form was processed successfully"

    def test_handle_slider_form_failed(self):
        service = CMSHomePageService()
        result = service.handle_form(
            form_type="slider_form",
            post_data={},
        )
        assert result["status"] is False
        assert isinstance(result["form"], HomePageSliderForm)
        assert result["detail"] == "Form processing failed"

    def test_handle_category_form_success(
        self,
        category_factory,
    ):
        service = CMSHomePageService()
        category = category_factory()
        result = service.handle_form(
            form_type="category_form",
            post_data={
                "category": category.pk,
                "component_type": "component_a",
                "order": 1,
            },
        )
        assert result["status"] is True
        assert isinstance(result["form"], HomePageCategoryForm)
        assert result["detail"] == "Form was processed successfully"

    def test_handle_category_form_failed(self):
        service = CMSHomePageService()
        result = service.handle_form(
            form_type="category_form",
            post_data={},
        )
        assert result["status"] is False
        assert isinstance(result["form"], HomePageCategoryForm)
        assert result["detail"] == "Form processing failed"

    def test_handle_form_invalid_type(self):
        service = CMSHomePageService()
        assert (
            service.handle_form(
                form_type="invalid",
                post_data={},
            )
            is None
        )
