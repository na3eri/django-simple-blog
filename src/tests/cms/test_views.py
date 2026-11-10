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
from django.contrib.messages import get_messages
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestCMSDashboardView:
    def test_view(self, client):
        response = client.get(
            reverse("cms_dashboard"),
        )
        assert response.status_code == 200
        assert response.templates[0].name == "cms/cms-dashboard.html"


class TestCMSHomePageView:
    def test_view(self, client):
        response = client.get(
            reverse("cms_homepage"),
        )
        assert response.status_code == 200
        assert response.templates[0].name == "cms/cms-home-page.html"
        assert "sliders" in response.context
        assert "categories" in response.context
        assert "slider_form" in response.context
        assert "category_form" in response.context
        assert isinstance(
            response.context["slider_form"],
            HomePageSliderForm,
        )
        assert isinstance(
            response.context["category_form"],
            HomePageCategoryForm,
        )

    def test_view_with_data(
        self,
        client,
        page_factory,
        home_page_slider_factory,
        home_page_category_factory,
    ):
        page = page_factory(
            name="home",
        )
        slider = home_page_slider_factory(
            page=page,
            order=1,
        )
        category = home_page_category_factory(
            page=page,
            order=1,
        )
        response = client.get(
            reverse("cms_homepage"),
        )
        assert response.status_code == 200
        assert list(response.context["sliders"]) == [slider]
        assert list(response.context["categories"]) == [category]


class TestCMSHomePageHandleSliderView:
    def test_get_redirects(self, client):
        response = client.get(
            reverse("cms_homepage_add_slider"),
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_homepage")

    def test_post_success(
        self,
        client,
        home_page_slider_factory,
    ):
        image = home_page_slider_factory.build().image
        response = client.post(
            reverse("cms_homepage_add_slider"),
            data={
                "title": "Test title",
                "subtitle": "Test subtitle",
                "alt_message": "Test alt",
                "url": "https://example.com/test",
                "order": 1,
                "image": image,
            },
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_homepage")
        assert HomePageSlider.objects.filter(
            title="Test title",
        ).exists()
        messages = list(
            get_messages(response.wsgi_request),
        )
        assert len(messages) == 1
        assert str(messages[0]) == "Form was processed successfully"
        assert messages[0].level == 25

    def test_post_invalid(self, client):
        response = client.post(
            reverse("cms_homepage_add_slider"),
            data={},
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_homepage")
        messages = list(
            get_messages(response.wsgi_request),
        )
        assert len(messages) == 1
        assert str(messages[0]) == "Form processing failed"
        assert messages[0].level == 40

    def test_post_edit(
        self,
        client,
        page_factory,
        home_page_slider_factory,
    ):
        page = page_factory(
            name="home",
        )
        slider = home_page_slider_factory(
            page=page,
            title="Old title",
            order=1,
        )
        image = home_page_slider_factory.build().image
        response = client.post(
            reverse(
                "cms_homepage_edit_slider",
                kwargs={"pk": slider.pk},
            ),
            data={
                "title": "Updated title",
                "subtitle": slider.subtitle,
                "alt_message": slider.alt_message,
                "url": slider.url,
                "order": 1,
                "image": image,
            },
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_homepage")
        slider.refresh_from_db()
        assert slider.title == "Updated title"


class TestCMSHomePageDeleteSliderView:
    def test_get_redirects(
        self,
        client,
        page_factory,
        home_page_slider_factory,
    ):
        page = page_factory(
            name="home",
        )
        slider = home_page_slider_factory(
            page=page,
            order=1,
        )
        response = client.get(
            reverse(
                "cms_homepage_delete_slider",
                kwargs={"pk": slider.pk},
            ),
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_homepage")
        assert HomePageSlider.objects.filter(
            pk=slider.pk,
        ).exists()

    def test_post_deletes_slider(
        self,
        client,
        page_factory,
        home_page_slider_factory,
    ):
        page = page_factory(
            name="home",
        )
        slider = home_page_slider_factory(
            page=page,
            order=1,
        )
        response = client.post(
            reverse(
                "cms_homepage_delete_slider",
                kwargs={"pk": slider.pk},
            ),
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_homepage")
        assert not HomePageSlider.objects.filter(
            pk=slider.pk,
        ).exists()
        messages = list(
            get_messages(response.wsgi_request),
        )
        assert len(messages) == 1
        assert str(messages[0]) == "Slider deleted successfully."
        assert messages[0].level == 25


class TestCMSHomePageHandleCategoryView:
    def test_get_redirects(self, client):
        response = client.get(
            reverse("cms_homepage_add_category"),
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_homepage")

    def test_post_success(
        self,
        client,
        category_factory,
    ):
        category = category_factory(
            name="test-category",
        )
        response = client.post(
            reverse("cms_homepage_add_category"),
            data={
                "category": category.pk,
                "component_type": "component_a",
                "order": 1,
            },
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_homepage")
        assert HomePageCategory.objects.filter(
            category=category,
        ).exists()
        messages = list(
            get_messages(response.wsgi_request),
        )
        assert len(messages) == 1
        assert str(messages[0]) == "Form was processed successfully"
        assert messages[0].level == 25

    def test_post_invalid(self, client):
        response = client.post(
            reverse("cms_homepage_add_category"),
            data={},
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_homepage")
        messages = list(
            get_messages(response.wsgi_request),
        )
        assert len(messages) == 1
        assert str(messages[0]) == "Form processing failed"
        assert messages[0].level == 40

    def test_post_edit(
        self,
        client,
        page_factory,
        home_page_category_factory,
        category_factory,
    ):
        page = page_factory(
            name="home",
        )
        old_category = category_factory(
            name="old-category",
        )
        new_category = category_factory(
            name="new-category",
        )
        instance = home_page_category_factory(
            page=page,
            category=old_category,
            order=1,
        )
        response = client.post(
            reverse(
                "cms_homepage_edit_category",
                kwargs={"pk": instance.pk},
            ),
            data={
                "category": new_category.pk,
                "component_type": "component_b",
                "order": 1,
            },
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_homepage")
        instance.refresh_from_db()
        assert instance.category == new_category
        assert instance.component_type == "component_b"


class TestCMSHomePageDeleteCategory:
    def test_get_redirects(
        self,
        client,
        page_factory,
        home_page_category_factory,
    ):
        page = page_factory(
            name="home",
        )
        instance = home_page_category_factory(
            page=page,
            order=1,
        )
        response = client.get(
            reverse(
                "cms_homepage_delete_category",
                kwargs={"pk": instance.pk},
            ),
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_homepage")
        assert HomePageCategory.objects.filter(
            pk=instance.pk,
        ).exists()

    def test_post_deletes_category(
        self,
        client,
        page_factory,
        home_page_category_factory,
    ):
        page = page_factory(
            name="home",
        )
        instance = home_page_category_factory(
            page=page,
            order=1,
        )
        response = client.post(
            reverse(
                "cms_homepage_delete_category",
                kwargs={"pk": instance.pk},
            ),
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_homepage")
        assert not HomePageCategory.objects.filter(
            pk=instance.pk,
        ).exists()
        messages = list(
            get_messages(response.wsgi_request),
        )
        assert len(messages) == 1
        assert str(messages[0]) == "Category deleted successfully."
        assert messages[0].level == 25


class TestCMSContactPageView:
    def test_get(self, client):
        response = client.get(
            reverse("cms_contactpage"),
        )
        assert response.status_code == 200
        assert response.templates[0].name == "cms/cms-contact-page.html"
        assert isinstance(
            response.context["form"],
            ContactPageDataForm,
        )

    def test_get_with_existing_data(
        self,
        client,
        page_factory,
        contact_page_data_factory,
    ):
        page = page_factory(
            name="contact",
        )
        instance = contact_page_data_factory(
            page=page,
        )
        response = client.get(
            reverse("cms_contactpage"),
        )
        assert response.status_code == 200
        assert response.context["form"].instance == instance

    def test_post_success(
        self,
        client,
        contact_page_data_factory,
    ):
        instance = contact_page_data_factory.build()
        response = client.post(
            reverse("cms_contactpage"),
            data={
                "address": instance.address,
                "email": instance.email,
                "phone_number": instance.phone_number,
                "linkedin_url": instance.linkedin_url,
                "instagram_url": instance.instagram_url,
                "x_url": instance.x_url,
                "facebook_url": instance.facebook_url,
                "map_url": instance.map_url,
            },
        )
        assert response.status_code == 200
        assert response.templates[0].name == "cms/cms-contact-page.html"
        assert isinstance(
            response.context["form"],
            ContactPageDataForm,
        )
        assert ContactPageData.objects.filter(
            email=instance.email,
        ).exists()
        messages = list(
            get_messages(response.wsgi_request),
        )
        assert len(messages) == 1
        assert str(messages[0]) == "Form was processed successfully"
        assert messages[0].level == 25

    def test_post_invalid(self, client):
        response = client.post(
            reverse("cms_contactpage"),
            data={},
        )
        assert response.status_code == 200
        assert response.templates[0].name == "cms/cms-contact-page.html"
        assert isinstance(
            response.context["form"],
            ContactPageDataForm,
        )
        messages = list(
            get_messages(response.wsgi_request),
        )
        assert len(messages) == 1
        assert str(messages[0]) == "Form processing failed"
        assert messages[0].level == 40


class TestCMSAboutPageView:
    def test_get(self, client):
        response = client.get(
            reverse("cms_aboutpage"),
        )
        assert response.status_code == 200
        assert response.templates[0].name == "cms/cms-about-page.html"
        assert isinstance(
            response.context["data_form"],
            AboutPageDataForm,
        )
        assert isinstance(
            response.context["image_form"],
            AboutPageImageForm,
        )
        assert list(response.context["images"]) == []

    def test_get_with_data(
        self,
        client,
        page_factory,
        about_page_data_factory,
        about_page_image_factory,
    ):
        page = page_factory(
            name="about",
        )
        data = about_page_data_factory(
            page=page,
        )
        image = about_page_image_factory(
            page=page,
        )
        response = client.get(
            reverse("cms_aboutpage"),
        )
        assert response.status_code == 200
        assert response.context["data_form"].instance == data
        assert isinstance(
            response.context["image_form"],
            AboutPageImageForm,
        )
        assert list(response.context["images"]) == [image]

    def test_post_success(
        self,
        client,
    ):
        response = client.post(
            reverse("cms_aboutpage"),
            data={
                "title": "Test title",
                "subtitle": "Test subtitle",
                "first_description": "First description",
                "second_description": "Second description",
                "third_description": "Third description",
            },
        )
        assert response.status_code == 200
        assert response.templates[0].name == "cms/cms-about-page.html"
        assert isinstance(
            response.context["data_form"],
            AboutPageDataForm,
        )
        assert isinstance(
            response.context["image_form"],
            AboutPageImageForm,
        )
        assert AboutPageData.objects.filter(
            title="Test title",
        ).exists()
        messages = list(
            get_messages(response.wsgi_request),
        )
        assert len(messages) == 1
        assert str(messages[0]) == "Form was processed successfully"
        assert messages[0].level == 25

    def test_post_invalid(self, client):
        response = client.post(
            reverse("cms_aboutpage"),
            data={},
        )
        assert response.status_code == 200
        assert response.templates[0].name == "cms/cms-about-page.html"
        assert isinstance(
            response.context["data_form"],
            AboutPageDataForm,
        )
        assert isinstance(
            response.context["image_form"],
            AboutPageImageForm,
        )
        messages = list(
            get_messages(response.wsgi_request),
        )
        assert len(messages) == 1
        assert str(messages[0]) == "Form processing failed"
        assert messages[0].level == 40


class TestCMSAboutPageHandleImageView:
    def test_get_redirects(self, client):
        response = client.get(
            reverse("cms_about_page_add_image"),
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_aboutpage")

    def test_post_success(
        self,
        client,
        about_page_image_factory,
    ):
        image = about_page_image_factory.build().image
        response = client.post(
            reverse("cms_about_page_add_image"),
            data={
                "alt_message": "Test alt message",
                "image": image,
            },
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_aboutpage")
        assert AboutPageImage.objects.filter(
            alt_message="Test alt message",
        ).exists()
        messages = list(
            get_messages(response.wsgi_request),
        )
        assert len(messages) == 1
        assert str(messages[0]) == "Form was processed successfully"
        assert messages[0].level == 25

    def test_post_invalid(self, client):
        response = client.post(
            reverse("cms_about_page_add_image"),
            data={},
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_aboutpage")
        messages = list(
            get_messages(response.wsgi_request),
        )
        assert len(messages) == 1
        assert str(messages[0]) == "Form processing failed"
        assert messages[0].level == 40

    def test_post_edit(
        self,
        client,
        page_factory,
        about_page_image_factory,
    ):
        page = page_factory(
            name="about",
        )
        instance = about_page_image_factory(
            page=page,
            alt_message="Old message",
        )
        image = about_page_image_factory.build().image
        response = client.post(
            reverse(
                "cms_about_page_edit_image",
                kwargs={"pk": instance.pk},
            ),
            data={
                "alt_message": "Updated message",
                "image": image,
            },
        )
        assert response.status_code == 302
        assert response.url == reverse("cms_aboutpage")
        instance.refresh_from_db()
        assert instance.alt_message == "Updated message"
