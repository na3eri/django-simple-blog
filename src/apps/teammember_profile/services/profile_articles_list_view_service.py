from django.db.models.query_utils import Q
from django.utils import timezone

from apps.blog.models import Article


class ProfileArticlesListService:
    def __init__(self, user, status, search_query=None):
        self.user = user
        self.user_profile = user.profile
        self.status = self.set_status(status)
        self.article_model = Article
        self.search_query = search_query

    @staticmethod
    def set_status(status: str):
        if not (status and isinstance(status, str)):
            return None

        if status.lower() not in ("all", "published", "draft"):
            return None

        return status.lower()

    def _get_total_articles(self):
        return (
            self.article_model.objects.filter(user_profile=self.user_profile).count()
            or 0
        )

    def _get_total_published_articles(self):
        return (
            self.article_model.objects.published()
            .filter(user_profile=self.user_profile)
            .count()
            or 0
        )

    def _get_total_draft_articles(self):
        return (
            self.article_model.objects.filter(
                Q(user_profile=self.user_profile)
                & Q(status=Article.StatusChoices.DRAFT)
            ).count()
            or 0
        )

    def get_articles(self):
        articles = None

        if self.status == "published":
            articles = self.article_model.objects.published().filter(
                user_profile=self.user_profile,
                is_deleted=False,
            )

        if self.status == "draft":
            articles = self.article_model.objects.filter(
                user_profile=self.user_profile,
                status=Article.StatusChoices.DRAFT,
                is_deleted=False,
            )

        if self.status == "all":
            articles = self.article_model.objects.filter(
                user_profile=self.user_profile,
                is_deleted=False,
            )

        if self.search_query:
            articles = articles.filter(
                title__icontains=self.search_query,
                excerpt__icontains=self.search_query,
                is_deleted=False,
            )

        return articles

    def get_context(self, view_context):
        context = {
            "profile_instance": self.user_profile,
            "total_articles": self._get_total_articles(),
            "total_published_articles": self._get_total_published_articles(),
            "total_draft_articles": self._get_total_draft_articles(),
            "status": self.status,
            "custom_range": view_context["paginator"].get_elided_page_range(
                number=view_context["page_obj"].number,
                on_each_side=2,
                on_ends=1,
            ),
        }
        return context

    def delete_article(self, article_id):
        try:
            article = self.article_model.objects.get(
                id=article_id,
                user_profile=self.user_profile,
            )
        except self.article_model.DoesNotExist:
            return False

        if article.is_deleted:
            return True

        article.is_deleted = True
        article.deleted_at = timezone.now()
        article.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
            ],
        )

        return True
