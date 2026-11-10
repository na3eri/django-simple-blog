from django.urls import path

from . import views

urlpatterns = [
    path(
        "cms/homepage/add/",
        views.cms_home_page_handle_slider_view,
        name="cms_homepage_add_slider",
    ),
    path(
        "cms/homepage/sliders/<int:pk>/edit/",
        views.cms_home_page_handle_slider_view,
        name="cms_homepage_edit_slider",
    ),
    path(
        "cms/homepage/sliders/<int:pk>/delete/",
        views.cms_home_page_delete_slider_view,
        name="cms_homepage_delete_slider",
    ),
    path(
        "cms/homepage/categories/add/",
        views.cms_home_page_handle_category_view,
        name="cms_homepage_add_category",
    ),
    path(
        "cms/homepage/categories/<int:pk>/edit/",
        views.cms_home_page_handle_category_view,
        name="cms_homepage_edit_category",
    ),
    path(
        "cms/homepage/categories/<int:pk>/delete/",
        views.cms_home_page_delete_category,
        name="cms_homepage_delete_category",
    ),
    path(
        "cms/about/images/add/",
        views.cms_about_page_handle_image_view,
        name="cms_about_page_add_image",
    ),
    path(
        "cms/about/images/<int:pk>/edit/",
        views.cms_about_page_handle_image_view,
        name="cms_about_page_edit_image",
    ),
    path("cms/about/", views.cms_about_page_view, name="cms_aboutpage"),
    path("cms/homepage/", views.cms_home_page_view, name="cms_homepage"),
    path("cms/contact/", views.cms_contact_page_view, name="cms_contactpage"),
    path("cms/dashboard/", views.cms_dashboard_view, name="cms_dashboard"),
]
