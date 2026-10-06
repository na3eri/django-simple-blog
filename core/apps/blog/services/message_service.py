from apps.blog.forms import MessageForm
from apps.blog.models import Message
from apps.users.models import Profile


class MessageService:
    def __init__(self):
        self.model = Message
        self.form = MessageForm

    def build_form(
        self,
        post_data=None,
        files_data=None,
        instance=None,
        user=None,
    ):
        if post_data is not None and user is not None and user.is_authenticated:
            post_data = post_data.copy()
            post_data["name"] = user.profile.full_name
            post_data["email"] = user.email

        return self.form(
            data=post_data,
            files=files_data,
            instance=instance,
        )

    def send_message(
        self,
        post_data=None,
        files_data=None,
        instance=None,
        user=None,
    ):
        form = self.build_form(
            post_data=post_data,
            files_data=files_data,
            instance=instance,
            user=user,
        )
        if not form.is_valid():
            return {
                "status": False,
                "form": form,
                "detail": "Form is invalid",
            }

        user_profile = None
        profile_id = form.cleaned_data.get("profile_id")
        if profile_id is not None:
            try:
                user_profile = Profile.objects.get(pk=profile_id)
            except Profile.DoesNotExist:
                user_profile = None

        parent_message = None
        parent_id = form.cleaned_data.get("parent_id")
        if parent_id is not None:
            try:
                parent_message = self.model.objects.get(pk=parent_id)
            except self.model.DoesNotExist:
                parent_message = None

        message = form.save(commit=False)

        if user_profile is not None:
            message.user_profile = user_profile

        if parent_message is not None:
            message.parent = parent_message

        message.save()

        return {
            "status": True,
            "form": form,
            "detail": "Message was sent",
        }
