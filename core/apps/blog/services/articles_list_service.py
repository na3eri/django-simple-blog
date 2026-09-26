from apps.blog.models import Article, Category
from apps.blog.utils import paginate_handler
from django.db.models.query_utils import Q
from taggit.models import Tag


class ArticleListPageService:
    def build_categories(self) -> list:
        return list(Category.objects.all())

    def build_recent_posts(self) -> list:
        return Article.objects.published()[:6]

    def build_tags(self) -> list:
        return list(Tag.objects.all()[:10])

    def build_articles(
        self,
        request,
        search: str | None = None,
        category: str | None = None,
        tag: str | None = None,
        results: int = 6,
    ):
        articles_queryset = Article.objects.published()

        if category is not None:
            articles_queryset = articles_queryset.by_category(category)

        if search is not None:
            articles_queryset = articles_queryset.filter(
                Q(title__icontains=search)
                | Q(excerpt__icontains=search)
                | Q(content__icontains=search)
            )

        if tag is not None:
            articles_queryset = articles_queryset.by_tag(tag)

        custom_range, articles = paginate_handler(
            request,
            articles_queryset,
            results,
        )
        return custom_range, articles
