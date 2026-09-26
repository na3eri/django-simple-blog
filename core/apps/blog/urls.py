from django.urls import path

from . import views

urlpatterns = [
    path("search/", views.articles_list_view, name="search_results"),
    path("tag/<slug:tag_slug>/", views.articles_list_view, name="tag"),
    path("category/<slug:category_slug>/", views.articles_list_view, name="category"),
    path("contact/", views.contact_view, name="contact"),
    path("about/", views.about_view, name="about"),
    path("<slug:slug>/", views.single_view, name="single"),
    path("", views.home_view, name="home"),
]
