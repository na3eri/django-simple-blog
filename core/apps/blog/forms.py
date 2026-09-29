from apps.blog.models import Comment
from django.forms import (
    EmailInput,
    HiddenInput,
    IntegerField,
    ModelForm,
    Textarea,
    TextInput,
)


class CommentForm(ModelForm):
    parent_id = IntegerField(
        required=False,
        widget=HiddenInput(),
    )

    class Meta:
        model = Comment
        fields = ["name", "email", "body"]
        widgets = {
            "name": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your name*",
                }
            ),
            "email": EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your email*",
                }
            ),
            "body": Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your Comment*",
                }
            ),
        }

    def __init__(self, *args, user_data=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user_data:
            self.fields["name"].required = False
            self.fields["email"].required = False

            self.fields["name"].initial = user_data["full_name"]
            self.fields["email"].initial = user_data["email"]
