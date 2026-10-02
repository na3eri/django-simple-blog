from apps.cms.models import HomePageCategory, HomePageSlider
from django.forms import (
    ClearableFileInput,
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
