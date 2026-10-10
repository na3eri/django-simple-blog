from django.db.models import Sum
from taggit.models import Tag

from apps.blog.models import Article, Comment
from apps.users.models import Profile


class PublicTeamMemberService:
    def __init__(self, profile_id):
        self.profile_model = Profile
        self.user_profile = self.get_profile(profile_id)

    def get_profile(self, pk):
        try:
            profile = self.profile_model.objects.get(id=pk)
        except self.profile_model.DoesNotExist:
            return None
        return profile

    def get_articles(self):
        return Article.objects.published().filter(user_profile=self.user_profile)

    def _get_total_views(self):
        views = (
            Article.objects.published()
            .filter(user_profile=self.user_profile)
            .aggregate(Sum("views"))["views__sum"]
        )
        views = int(views) / 1000 if views else 0
        return views if views > 1000 else 0

    def get_context(self, view_context) -> dict:
        return {
            "profile_instance": self.user_profile,
            "total_views": self._get_total_views(),
            "total_comments": Comment.objects.approved()
            .filter(article__user_profile=self.user_profile)
            .count(),
            "tags": list(Tag.objects.all()[:10]),
            "recent_posts": Article.objects.published().filter(
                user_profile=self.user_profile
            )[:4],
            "custom_range": view_context["paginator"].get_elided_page_range(
                number=view_context["page_obj"].number,
                on_each_side=2,
                on_ends=1,
            ),
        }
