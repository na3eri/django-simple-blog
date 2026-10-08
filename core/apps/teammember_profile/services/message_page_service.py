from django.db.models import Q

from apps.blog.models import Message
from apps.users.models import Profile


class MessagePageService:
    def __init__(self, user_id):
        self.user = self.get_user(user_id)
        self.user_profile = self.get_profile(user_id)

    @staticmethod
    def get_user(user_id):
        try:
            return Profile.objects.select_related("user").get(user_id=user_id).user
        except Profile.DoesNotExist:
            return None

    @staticmethod
    def get_profile(user_id):
        try:
            return Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            return None

    def get_messages(self):
        if self.user is None or self.user_profile is None:
            return Message.objects.none()

        if self.user.is_superuser:
            return Message.objects.filter(
                Q(user_profile=self.user_profile) | Q(user_profile__isnull=True)
            )

        return Message.objects.filter(user_profile=self.user_profile)

    def get_context(self, view_context):
        return {
            "profile_instance": self.user_profile,
            "messages": self.get_messages(),
        }
