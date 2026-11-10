import pytest
from apps.blog.forms import CommentForm


class TestCommentForm:
    def test_valid_data(self):
        form = CommentForm(
            data={
                "name": "test",
                "email": "test@example.com",
                "body": "comment body",
            }
        )

        assert form.is_valid()

    def test_user_data(self):
        form = CommentForm(
            data={
                "name": "test",
                "email": "test@example.com",
                "body": "comment body",
            },
            user_data={
                "full_name": "test user_data",
                "email": "testUserData@example.com",
            },
        )

        assert form.is_valid()
