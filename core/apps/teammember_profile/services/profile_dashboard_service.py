from django.db.models import Sum

from apps.blog.models import Article, Message, Comment
from apps.users.models import Profile


class ProfileDashboardService:
    def __init__(self, profile_id):
        self.user_profile = self.get_profile(profile_id)
        self.article_model = Article
        self.message_model = Message
        self.comment_model = Comment

    def get_profile(self, profile_id):
        try:
            profile = Profile.objects.get(pk=profile_id)
        except Profile.DoesNotExist:
            profile = None
        return profile

    def _get_recent_articles(self):
        return self.article_model.objects.published().filter(
            user_profile=self.user_profile
        )[:4]

    def _get_latest_messages(self):
        return (
            self.message_model.objects.active()
            .unread()
            .filter(user_profile=self.user_profile)[:3]
        )

    def _get_latest_comments(self):
        return self.comment_model.objects.filter(
            article__user_profile=self.user_profile,
        )[:3]

    def _get_total_views(self):
        return (
            int(
                self.article_model.objects.published()
                .filter(user_profile=self.user_profile)
                .aggregate(Sum("views"))["views__sum"]
                / 1000
            )
            or 0
        )

    def _get_total_comments(self):
        return (
            self.comment_model.objects.approved()
            .filter(article__user_profile=self.user_profile)
            .count()
            or 0
        )

    def _get_total_pending_comment(self):
        return (
            self.comment_model.objects.filter(
                article__user_profile=self.user_profile
            ).count()
            or 0
        )

    def _get_total_articles(self):
        return (
            self.article_model.objects.published()
            .filter(user_profile=self.user_profile)
            .count()
            or 0
        )

    def _get_total_messages(self):
        return (
            self.message_model.objects.active()
            .filter(user_profile=self.user_profile)
            .count()
            or 0
        )

    def _get_total_unread_messages(self):
        return (
            self.message_model.objects.active()
            .unread()
            .filter(user_profile=self.user_profile)
            .count()
            or 0
        )

    def get_context(self, view_context):
        return {
            "profile_instance": self.user_profile,
            "total_articles": self._get_total_articles(),
            "total_views": self._get_total_views(),
            "total_comments": self._get_total_comments(),
            "total_messages": self._get_total_messages(),
            "total_pending_comments": self._get_total_pending_comment(),
            "total_unread_messages": self._get_total_unread_messages(),
            "recent_articles": self._get_recent_articles(),
            "latest_messages": self._get_latest_messages(),
            "latest_comments": self._get_latest_comments(),
        }
