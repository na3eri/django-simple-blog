import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestUsersSigninView:
    def test_signin_url(self, client):
        url = reverse("signin")
        response = client.get(url)
        assert response.status_code == 200

    def test_signed_in_redirect(self, client, user):
        client.force_login(user)
        url = reverse("signin")
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == "/"

    def test_signin_success(self, client, user):
        url = reverse("signin")
        response = client.post(
            url,
            {
                "email": "test@example.com",
                "password": "test",
            },
        )
        assert response.status_code == 302
        assert response.url == "/"
        assert client.session["_auth_user_id"] == str(user.pk)

    def test_remember_off_session_expiry(self, client, user):
        url = reverse("signin")
        response = client.post(
            url,
            {
                "email": "test@example.com",
                "password": "test",
            },
        )
        assert response.status_code == 302
        assert response.url == "/"
        assert client.session["_auth_user_id"] == str(user.pk)
        assert client.session.get_expiry_age() == 300

    def test_remember_on_session_expiry(self, client, user):
        url = reverse("signin")
        response = client.post(
            url,
            {
                "email": "test@example.com",
                "password": "test",
                "remember": "on",
            },
        )
        assert response.status_code == 302
        assert response.url == "/"
        assert client.session["_auth_user_id"] == str(user.pk)
        assert client.session.get_expiry_age() == 60 * 60 * 24 * 30

    def test_invalid_credentials(self, client, user):
        url = reverse("signin")
        response = client.post(
            url,
            {
                "email": "invalid@example.com",
                "password": "invalid-password",
            },
        )
        assert response.status_code == 302
        assert response.url == "/signin/"
