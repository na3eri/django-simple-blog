from apps.blog.models import Comment, Message
from django.forms import (
    EmailInput,
    HiddenInput,
    IntegerField,
    ModelForm,
    Textarea,
    TextInput,
    Select,
)

from django.forms import (
    ClearableFileInput,
    CheckboxInput,
)

from apps.blog.models import Article


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


class MessageForm(ModelForm):
    profile_id = IntegerField(required=False, widget=HiddenInput())
    parent_id = IntegerField(required=False, widget=HiddenInput())

    class Meta:
        model = Message
        fields = [
            "name",
            "email",
            "subject",
            "topic",
            "body",
        ]
        widgets = {
            "name": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your Name",
                    "required": True,
                }
            ),
            "email": EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your Email",
                    "required": True,
                }
            ),
            "subject": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Subject",
                    "required": True,
                }
            ),
            "topic": Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "body": Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Write your message...",
                    "required": True,
                }
            ),
        }


class ArticleForm(ModelForm):
    class Meta:
        model = Article

        fields = [
            "title",
            "category",
            "tags",
            "image",
            "excerpt",
            "content",
            "status",
            "is_comment_enabled",
        ]

        widgets = {
            "title": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "article-title",
                    "placeholder": "Enter a compelling headline...",
                }
            ),
            "category": Select(
                attrs={
                    "class": "form-select",
                    "id": "article-category",
                }
            ),
            "tags": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "article-tags",
                    "placeholder": "e.g. Tips, Marketing, Creative",
                }
            ),
            "image": ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "id": "article-image",
                    "accept": "image/*",
                }
            ),
            "excerpt": Textarea(
                attrs={
                    "class": "form-control",
                    "id": "article-excerpt",
                    "rows": 3,
                    "placeholder": (
                        "A short 1–2 sentence summary shown on listing pages..."
                    ),
                }
            ),
            "content": Textarea(
                attrs={
                    "class": "form-control",
                    "id": "article-content",
                    "rows": 10,
                    "placeholder": "Write your article here...",
                }
            ),
            "status": Select(
                attrs={
                    "class": "form-select",
                    "id": "article-status",
                }
            ),
            "is_comment_enabled": CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "id": "allow-comments",
                }
            ),
        }
