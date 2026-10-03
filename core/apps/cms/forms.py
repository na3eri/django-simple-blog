from apps.cms.models import (
    AboutPageData,
    AboutPageImage,
    ContactPageData,
    HomePageCategory,
    HomePageSlider,
)
from django.db.models import TextField
from django.forms import (
    ClearableFileInput,
    EmailInput,
    ModelForm,
    NumberInput,
    Select,
    TextInput,
    URLInput,
)


class HomePageSliderForm(ModelForm):
    class Meta:
        model = HomePageSlider
        fields = [
            "title",
            "subtitle",
            "alt_message",
            "url",
            "order",
            "image",
        ]
        widgets = {
            "title": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "slider-title",
                    "placeholder": "Slider title",
                }
            ),
            "subtitle": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "slider-subtitle",
                    "placeholder": "Slider subtitle",
                }
            ),
            "alt_message": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "slider-alt",
                    "placeholder": "Image alt text",
                }
            ),
            "url": URLInput(
                attrs={
                    "class": "form-control",
                    "id": "slider-url",
                    "placeholder": "/page-url",
                }
            ),
            "order": NumberInput(
                attrs={
                    "class": "form-control",
                    "id": "slider-order",
                    "min": 1,
                    "max": 4,
                    "placeholder": "1",
                }
            ),
            "image": ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                    "data-preview": "true",
                }
            ),
        }


class HomePageCategoryForm(ModelForm):
    class Meta:
        model = HomePageCategory

        fields = [
            "category",
            "component_type",
            "order",
        ]

        widgets = {
            "category": Select(
                attrs={
                    "class": "form-select",
                    "id": "category-name",
                }
            ),
            "component_type": Select(
                attrs={
                    "class": "form-select",
                    "id": "category-component",
                }
            ),
            "order": NumberInput(
                attrs={
                    "class": "form-control",
                    "id": "category-order",
                    "min": 1,
                    "max": 3,
                    "placeholder": "1",
                }
            ),
        }


class ContactPageDataForm(ModelForm):
    class Meta:
        model = ContactPageData
        fields = [
            "address",
            "email",
            "phone_number",
            "linkedin_url",
            "instagram_url",
            "x_url",
            "facebook_url",
            "map_url",
        ]
        widgets = {
            "address": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "contact-address",
                    "placeholder": "A108 Adam Street, New York, NY 535022",
                }
            ),
            "email": EmailInput(
                attrs={
                    "class": "form-control",
                    "id": "contact-email",
                    "placeholder": "youremail@example.com",
                }
            ),
            "phone_number": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "contact-phone",
                    "placeholder": "+989999999999",
                }
            ),
            "linkedin_url": URLInput(
                attrs={
                    "class": "form-control",
                    "id": "contact-linkedin",
                    "placeholder": "https://linkedin.com/in/yourusername/",
                }
            ),
            "instagram_url": URLInput(
                attrs={
                    "class": "form-control",
                    "id": "contact-instagram",
                    "placeholder": "https://instagram.com/yourusername/",
                }
            ),
            "x_url": URLInput(
                attrs={
                    "class": "form-control",
                    "id": "contact-x",
                    "placeholder": "https://x.com/yourusername/",
                }
            ),
            "facebook_url": URLInput(
                attrs={
                    "class": "form-control",
                    "id": "contact-facebook",
                    "placeholder": "https://facebook.com/yourusername/",
                }
            ),
            "map_url": URLInput(
                attrs={
                    "class": "form-control",
                    "id": "contact-map",
                    "placeholder": "https://www.google.com/maps/something/",
                }
            ),
        }


class AboutPageImageForm(ModelForm):
    class Meta:
        model = AboutPageImage
        fields = [
            "image",
            "alt_message",
        ]
        widgets = {
            "image": ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "id": "image-upload",
                    "accept": "image/*",
                    "data-preview": "true",
                }
            ),
            "alt_message": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "image-alt",
                    "placeholder": "Image alt text",
                }
            ),
        }


class AboutPageDataForm(ModelForm):
    class Meta:
        model = AboutPageData
        fields = [
            "title",
            "subtitle",
            "first_description",
            "second_description",
            "third_description",
        ]
        widgets = {
            "title": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "about-title",
                    "placeholder": "Title",
                }
            ),
            "subtitle": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "about-subtitle",
                    "placeholder": "Subtitle",
                }
            ),
            "first_description": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "about-desc1",
                    "placeholder": "First description",
                }
            ),
            "second_description": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "about-desc2",
                    "placeholder": "Second description",
                }
            ),
            "third_description": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "about-desc3",
                    "placeholder": "Third description",
                }
            ),
        }
