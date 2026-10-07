from apps.blog.models import Article
from apps.users.models import Profile


class ProfileCreateArticleService:
    def __init__(self, profile_id, article_id=None):
        self.user_profile = self.get_object_or_none(Profile, profile_id)
        self.article = self.get_object_or_none(Article, article_id)
        self.article_model = Article

    @staticmethod
    def get_object_or_none(model, instance_id):
        if instance_id is None:
            return None

        try:
            instance = model.objects.get(pk=instance_id)
        except model.DoesNotExist:
            instance = None
        return instance

    def get_context(self, view_context):
        return {
            "profile_instance": self.user_profile,
        }

    def set_article(self, article_instance):
        self.article = article_instance
