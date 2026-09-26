from apps.blog.forms import CommentForm
from apps.blog.models import Article
from apps.blog.services.aboutpage_service import AboutPageService
from apps.blog.services.article_service import ArticleService
from apps.blog.services.articles_list_service import ArticleListPageService
from apps.blog.services.contact_service import ContactPageService
from apps.blog.services.homepage_service import HomePageService
from apps.cms.models import HomePageCategory, HomePageSlider
from django.shortcuts import get_object_or_404, redirect, render


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

    context = {
        "article": article,
    }
    return render(request, "blog/single-post.html", context)


def about_view(request):
    service = AboutPageService()

    context = {
        "about_data": service.build_data(),
        "about_images": service.build_images(),
        "team_members": service.build_team(),
    }
    return render(request, "blog/about.html", context)


def contact_view(request):
    service = ContactPageService()

    context = {
        "contact_data": service.build_data(),
    }
    return render(request, "blog/contact.html", context)


def articles_list_view(request, category_slug=None, tag_slug=None):
    service = ArticleListPageService()
    search_query = request.GET.get("q")

    if search_query:
        custom_range, articles = service.build_articles(
            request=request,
            search=search_query,
        )
        title = f"Search: {search_query}"
        place = f'Search <li><a href="#"></a></li> {search_query}'

    elif category_slug:
        custom_range, articles = service.build_articles(
            request=request,
            category=category_slug,
        )
        title = f"Category: {category_slug}"
        place = f'Category <li><a href="#"></a></li> {category_slug}'

    elif tag_slug:
        custom_range, articles = service.build_articles(
            request=request,
            tag=tag_slug,
        )
        title = f"Tag: {tag_slug}"
        place = f'Tag <li><a href="#"></a></li> {tag_slug}'

    else:
        custom_range, articles = service.build_articles(
            request=request,
        )
        title = "All Articles"
        place = "All Articles"

    context = {
        "title": title,
        "place": place,
        "articles": articles,
        "custom_range": custom_range,
        "categories": service.build_categories(),
        "recent_posts": service.build_recent_posts(),
        "tags": service.build_tags(),
    }

    return render(
        request,
        "blog/articles-list.html",
        context,
    )


def single_view(request, slug):
    article_service = ArticleService()
    article_list_service = ArticleListPageService()

    article = article_service.get_published_article(slug)

    context = {
        "article": article,
        "categories": article_list_service.build_categories(),
        "recent_posts": article_list_service.build_recent_posts(),
        "tags": article_list_service.build_tags(),
        "form": article_service.build_form(),
        "comments": article_service.get_comments(article),
    }

    if request.method == "POST":
        user_data = None

        if request.user.is_authenticated:
            user_data = {
                "full_name": request.user.profile.full_name,
                "email": request.user.profile.email,
                "user_profile": request.user.profile,
            }

        result = article_service.handle_comment(
            request.POST,
            article,
            user_data,
        )

        if result["status"]:
            return redirect(article.get_absolute_url())

        context["form"] = result["form"]

    return render(
        request,
        "blog/single-post.html",
        context,
    )
