# forms.py

from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.forms import Textarea, URLInput, TextInput, FileInput
from django.forms.models import ModelForm

from apps.users.models import Profile


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email",
                "id": "email",
                "required": True,
            }
        )
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your password",
                "id": "password1",
                "required": True,
            }
        )
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your password",
                "id": "password2",
                "required": True,
            }
        )
    )


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = [
            "image",
            "full_name",
            "short_bio",
            "linkedin_url",
            "instagram_url",
            "x_url",
            "facebook_url",
        ]
        widgets = {
            "image": FileInput(
                attrs={
                    "id": "avatar-upload",
                    "class": "d-none",
                    "accept": "image/*",
                }
            ),
            "full_name": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Image alt text",
                }
            ),
            "short_bio": Textarea(
                attrs={
                    "class": "form-control",
                    "id": "bio",
                    "rows": 3,
                    "placeholder": (
                        "A short 1–2 sentence summary shown on listing pages..."
                    ),
                }
            ),
            "linkedin_url": URLInput(
                attrs={
                    "class": "form-control",
                    "id": "social-linkedin",
                    "placeholder": "https://linkedin.com/in/yourusername/",
                }
            ),
            "instagram_url": URLInput(
                attrs={
                    "class": "form-control",
                    "id": "social-instagram",
                    "placeholder": "https://instagram.com/yourusername/",
                }
            ),
            "x_url": URLInput(
                attrs={
                    "class": "form-control",
                    "id": "social-x",
                    "placeholder": "https://x.com/yourusername/",
                }
            ),
            "facebook_url": URLInput(
                attrs={
                    "class": "form-control",
                    "id": "social-facebook",
                    "placeholder": "https://facebook.com/yourusername/",
                }
            ),
        }
