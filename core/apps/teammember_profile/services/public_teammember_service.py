from django.db.models import Sum
from taggit.models import Tag

from apps.blog.models import Article, Comment
from apps.users.models import Profile


class PublicTeamMemberService:
    def __init__(self, user):
        self.profile_model = Profile
        self.user = user
        self.user_profile = user.profile

    def get_articles(self):
        return Article.objects.published().filter(user_profile=self.user_profile)

    def get_context(self, view_context) -> dict:
        return {
            "profile_instance": self.user_profile,
            "total_views": int(
                Article.objects.published()
                .filter(user_profile=self.user_profile)
                .aggregate(Sum("views"))["views__sum"]
                / 1000
            )
            or 0,
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
