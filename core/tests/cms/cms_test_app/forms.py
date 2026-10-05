from django import forms

from tests.cms.cms_test_app.models import TestServiceModel


class TestServiceModelForm(forms.ModelForm):
    class Meta:
        model = TestServiceModel
        fields = ["title"]
