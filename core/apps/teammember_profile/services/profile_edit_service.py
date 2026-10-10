from apps.users.models import Profile


class ProfileEditService:
    def __init__(self, user):
        self.model = Profile
        self.user = user
        self.user_profile = user.profile

    def get_queryset(self):
        return Profile.objects.filter(user=self.user)

    def get_context(self, view_context):
        return {
            "profile_instance": self.user_profile,
        }
