from apps.blog.models import Article
from apps.users.models import Profile


class ProfileArticleService:
    def __init__(self, user_id, article_id=None):
        self.user_profile = self.get_profile_by_user_id(user_id)
        self.article = self.get_object_or_none(Article, article_id)
        self.article_model = Article

    @staticmethod
    def get_profile_by_user_id(user_id):
        try:
            return Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            return None

    @staticmethod
    def get_object_or_none(model, instance_id):
        if instance_id is None:
            return None

        try:
            return model.objects.get(pk=instance_id)
        except model.DoesNotExist:
            return None

    def get_context(self, view_context):
        return {
            "profile_instance": self.user_profile,
        }

    def set_article(self, article_instance):
        self.article = article_instance

    def get_article_queryset(self, article_pk):
        return self.article_model.objects.filter(
            user_profile=self.user_profile,
            id=article_pk,
        )
