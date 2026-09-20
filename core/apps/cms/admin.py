from django.contrib import admin

from .models import (
    AboutPageData,
    AboutPageImage,
    ContactPageData,
    HomePageCategory,
    HomePageSlider,
    Page,
)


class AboutPageDataInline(admin.StackedInline):
    model = AboutPageData
    extra = 0
    max_num = 1


class AboutPageImageInline(admin.TabularInline):
    model = AboutPageImage
    extra = 0

    def has_add_permission(self, request, obj=None):
        if obj is None:
            return True

        return obj.about_page_images.count() < 3


class ContactPageDataInline(admin.StackedInline):
    model = ContactPageData
    extra = 0
    max_num = 1


class HomePageSliderInline(admin.TabularInline):
    model = HomePageSlider
    extra = 0

    def has_add_permission(self, request, obj=None):
        if obj is None:
            return True

        return obj.home_page_sliders.count() < 4


class HomePageCategoryInline(admin.TabularInline):
    model = HomePageCategory
    extra = 0

    def has_add_permission(self, request, obj=None):
        if obj is None:
            return True

        return obj.home_page_categories.count() < 3


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []

        page_name = obj.name.strip().lower()

        if page_name == "home":
            inline_classes = [
                HomePageSliderInline,
                HomePageCategoryInline,
            ]

        elif page_name == "about":
            inline_classes = [
                AboutPageDataInline,
                AboutPageImageInline,
            ]

        elif page_name == "contact":
            inline_classes = [
                ContactPageDataInline,
            ]

        else:
            inline_classes = []

        return [inline(self.model, self.admin_site) for inline in inline_classes]
