import factory
import pytest
from apps.cms.admin import (
    AboutPageImageInline,
    HomePageSliderInline,
    HomePageCategoryInline,
    PageAdmin,
    AboutPageDataInline,
    ContactPageDataInline,
)
from apps.cms.models import Page
from django.contrib import admin
from django.test import RequestFactory

pytestmark = pytest.mark.django_db


class TestAboutPageImageInline:
    def test_has_add_permission_without_object(
        self, page_factory, about_page_image_factory
    ):
        inline = AboutPageImageInline(
            Page,
            admin.site,
        )
        request = RequestFactory().get("/admin/")

        assert (
            inline.has_add_permission(
                request,
                obj=None,
            )
            is True
        )

        about_page = page_factory(id=1, name="about")
        about_page_image_factory.create_batch(
            3,
            page=about_page,
            image=factory.django.ImageField(filename="test-image-1.jpg"),
        )

        assert (
            inline.has_add_permission(
                request,
                obj=about_page,
            )
            is False
        )


class TestHomePageSliderInline:
    def test_has_add_permission_without_object(
        self, page_factory, home_page_slider_factory
    ):
        inline = HomePageSliderInline(
            Page,
            admin.site,
        )
        request = RequestFactory().get("/admin/")

        assert (
            inline.has_add_permission(
                request,
                obj=None,
            )
            is True
        )

        home_page = page_factory(id=1, name="home")
        home_page_slider_factory.create_batch(
            4,
            page=home_page,
            order=factory.Sequence(lambda n: n),
            image=factory.django.ImageField(filename="test-image-1.jpg"),
        )
        assert (
            inline.has_add_permission(
                request,
                obj=home_page,
            )
            is False
        )


class TestHomePageCategoryInline:
    def test_has_add_permission_without_object(
        self, page_factory, category_factory, home_page_category_factory
    ):
        inline = HomePageCategoryInline(
            Page,
            admin.site,
        )
        request = RequestFactory().get("/admin/")

        assert (
            inline.has_add_permission(
                request,
                obj=None,
            )
            is True
        )

        home_page = page_factory(id=1, name="home")

        categories = []
        for i in range(3):
            category = category_factory(id=i, name=f"category-{i}")
            categories.append(category)

        home_page_category_factory.create_batch(
            3,
            page=home_page,
            category=factory.Iterator(categories),
            order=factory.Sequence(lambda n: n),
        )

        assert (
            inline.has_add_permission(
                request,
                obj=home_page,
            )
            is False
        )


class TestPageAdmin:
    def test_get_inline_instances(
        self,
        page_factory,
    ):
        page_admin = PageAdmin(
            Page,
            admin.site,
        )
        request = RequestFactory().get("/admin/")

        assert (
            page_admin.get_inline_instances(
                request,
                obj=None,
            )
            == []
        )

        home_page = page_factory(name="home")
        inlines = page_admin.get_inline_instances(
            request,
            obj=home_page,
        )

        assert len(inlines) == 2
        assert isinstance(
            inlines[0],
            HomePageSliderInline,
        )
        assert isinstance(
            inlines[1],
            HomePageCategoryInline,
        )

        about_page = page_factory(name="about")
        inlines = page_admin.get_inline_instances(
            request,
            obj=about_page,
        )

        assert len(inlines) == 2
        assert isinstance(
            inlines[0],
            AboutPageDataInline,
        )
        assert isinstance(
            inlines[1],
            AboutPageImageInline,
        )

        contact_page = page_factory(name="contact")
        inlines = page_admin.get_inline_instances(
            request,
            obj=contact_page,
        )

        assert len(inlines) == 1
        assert isinstance(
            inlines[0],
            ContactPageDataInline,
        )

        unknown_page = page_factory(name="unknown")
        inlines = page_admin.get_inline_instances(
            request,
            obj=unknown_page,
        )

        assert len(inlines) == 0
        assert isinstance(inlines, list)
        assert not inlines
