from apps.blog.models import Article


class ArticleService:
    @staticmethod
    def get_published_article(slug: str):
        try:
            return Article.objects.published().by_slug(slug)
        except Article.DoesNotExist:
            raise Http404
