import pytest

pytestmark = pytest.mark.django_db


class TestPageModel:
    def test_str_method(self, page_factory):
        page = page_factory()
        assert page.__str__() == page.name


class TestContactPageDataModel:
    def test_str_method(self, contact_page_data_factory, page_factory):
        contact_page = page_factory(name="contact")
        instance = contact_page_data_factory(page=contact_page)
        assert instance.__str__() == f"Page: {instance.page.name} - Contact Data"


class TestAboutPageDataModel:
    def test_str_method(self, about_page_data_factory, page_factory):
        page = page_factory(name="about")
        instance = about_page_data_factory(page=page)
        assert instance.__str__() == f"Page: {instance.page.name} - About Data"


class TestAboutPageImageModel:
    def test_str_method(self, about_page_image_factory, page_factory):
        page = page_factory(name="about")
        instance = about_page_image_factory(page=page)
        assert (
            instance.__str__()
            == f"{instance.id} - Page: {instance.page.name} - About Image"
        )


class TestHomePageSliderModel:
    def test_str_method(self, home_page_slider_factory, page_factory):
        page = page_factory(name="home")
        instance = home_page_slider_factory(page=page)

        assert (
            instance.__str__()
            == f"{instance.id} - Title: {instance.title} - Page: {instance.page.name} - Home Slider"
        )


class TestHomePageCategoryModel:
    def test_str_method(self, home_page_category_factory, page_factory):
        page = page_factory(name="home")
        instance = home_page_category_factory(page=page)

        assert (
            instance.__str__()
            == f"{instance.id} - Page: {instance.page.name} - Category: {instance.category.name} - Home Category"
        )
