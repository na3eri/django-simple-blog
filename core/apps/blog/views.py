from apps.blog.models import Article
from apps.blog.services.article_service import ArticleService
from apps.blog.services.homepage_service import HomePageService
from apps.cms.models import HomePageCategory, HomePageSlider
from django.shortcuts import get_object_or_404, render


# Create your views here.
def home_view(request):
    service = HomePageService()

    context = {
        "sliders": service.build_slider(),
        "popular": service.build_popular(),
        "components": service.build_all_components(),
    }
    return render(request, "blog/home.html", context)


def about_view(request):
    return render(request, "blog/about.html")


def single_view(request, slug):
    service = ArticleService()
    article = service.get_published_article(slug)
    return render(request, "blog/single-post.html")
