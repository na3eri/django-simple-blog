import pytest
from apps.users.models import User

pytestmark = pytest.mark.django_db


class TestUserManager:
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="test",
        )

        assert user.pk is not None
        assert user.email == "test@example.com"

    def test_create_user_email_field(self):
        with pytest.raises(ValueError, match="The email field must be set."):
            User.objects.create_user(
                email="",
                password="test",
            )

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email="test@example.com",
            password="test",
        )

        assert superuser.pk is not None
        assert superuser.email == "test@example.com"
        assert superuser.is_staff == True
        assert superuser.is_superuser == True

    def test_create_superuser_is_staff_field(self):
        with pytest.raises(
            ValueError,
            match="Superuser must have is_staff=True.",
        ):
            User.objects.create_superuser(
                email="test@example.com",
                password="test",
                is_staff=False,
            )

    def test_create_superuser_is_superuser_field(self):
        with pytest.raises(
            ValueError,
            match="Superuser must have is_superuser=True.",
        ):
            User.objects.create_superuser(
                email="test@example.com",
                password="test",
                is_superuser=False,
            )
