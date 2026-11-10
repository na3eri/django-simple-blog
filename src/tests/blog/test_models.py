import pytest

pytestmark = pytest.mark.django_db


class TestCategoryModel:
    def test_str_method(self, category_factory):
        category = category_factory()
        assert category.__str__() == "test"

    def test_save_method(self, category_factory):
        category = category_factory(name="test slug")
        assert category.slug == "test-slug"


class TestArticleModel:
    def test_str_method(self, article_factory):
        article = article_factory()
        assert article.__str__() == "test"

    def test_get_absolute_url(self, article_factory):
        article = article_factory(title="test article")
        assert article.get_absolute_url() == "/test-article/"

    def test_duplicate_slug(self, article_factory, category_factory):
        first_article = article_factory(title="duplicate article")

        category = category_factory(name="test2")
        second_article = article_factory(title="duplicate article", category=category)

        assert first_article.slug == "duplicate-article"
        assert second_article.slug == "duplicate-article-2"


class TestCommentModel:
    def test_str_method(self, comment_factory):
        comment = comment_factory(
            name="test",
            email="test@example.com",
            body="comment test body",
        )
        assert comment.__str__() == "test"


class TestMessageModel:
    def test_str_method(self, message_factory):
        message = message_factory(
            name="test name",
            email="test@example.com",
            subject="test",
            body="message test body",
        )
        assert message.__str__() == "test name"
