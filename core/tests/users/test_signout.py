import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestUsersSignoutView:
    def test_signout_url(self, client):
        url = reverse("signout")
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == "/"

    def test_signout_functionality(self, client, user):
        client.force_login(user)
        url = reverse("signout")
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == "/"
        assert response.wsgi_request.user.is_authenticated == False
