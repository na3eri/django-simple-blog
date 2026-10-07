from django.db.models.query_utils import Q

from apps.blog.models import Article
from apps.users.models import Profile


class ProfileArticlesListService:
    def __init__(self, profile_id, status, search_query=None):
        self.user_profile = self.get_profile(profile_id)
        self.status = self.set_status(status)
        self.article_model = Article
        self.search_query = search_query

    @staticmethod
    def get_profile(profile_id):
        try:
            profile = Profile.objects.get(pk=profile_id)
        except Profile.DoesNotExist:
            profile = None
        return profile

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
                user_profile=self.user_profile
            )

        if self.status == "draft":
            articles = self.article_model.objects.filter(
                Q(user_profile=self.user_profile)
                & Q(status=Article.StatusChoices.DRAFT)
            )

        if self.status == "all":
            articles = self.article_model.objects.filter(user_profile=self.user_profile)

        if self.search_query:
            articles = articles.filter(
                Q(title__icontains=self.search_query)
                | Q(excerpt__icontains=self.search_query)
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
