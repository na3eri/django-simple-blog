from apps.blog.services.message_service import MessageService
from apps.users.models import Profile


class MessagePageService:
    def __init__(self, profile_id):
        self.user_profile = self.get_profile(profile_id)
        self.message_service = MessageService()

    def get_profile(self, profile_id):
        try:
            instance = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            instance = None
        return instance

    def get_context(self, view_context):
        return {
            "profile_instance": self.user_profile,
        }
