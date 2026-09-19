import pytest

pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_str_return(self, user_factory):
        user = user_factory()
        assert user.__str__() == "test@example.com"


class TestProfile:
    def test_str_return(self, profile_factory):
        profile = profile_factory()
        assert (
            profile.__str__()
            == f"{profile.id} | {profile.email} | {profile.role} | {profile.job_title} | {profile.updated_at}"
        )
