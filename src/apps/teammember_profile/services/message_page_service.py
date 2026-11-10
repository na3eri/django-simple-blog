from django.db.models import Q

from apps.blog.models import Message


class MessagePageService:
    def __init__(self, user):
        self.user = user
        self.user_profile = user.profile

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
        }
