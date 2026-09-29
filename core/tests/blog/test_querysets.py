import pytest
from apps.blog.models import Article, Comment

pytestmark = pytest.mark.django_db


class TestArticleQueryset:
    def test_published_method(self, article_factory, category_factory):
        first_article = article_factory(
            title="first article",
            status=Article.StatusChoices.PUBLISHED,
        )
        category = category_factory(name="forSecondArticle")
        second_article = article_factory(
            title="second article",
            status=Article.StatusChoices.DRAFT,
            category=category,
        )
        queryset = Article.objects.published()

        assert queryset.count() == 1
        assert queryset.first() == first_article

    def test_popular_method(self, article_factory, category_factory):
        first_article = article_factory(
            title="first article popular",
            status=Article.StatusChoices.PUBLISHED,
        )
        second_category = category_factory(name="forSecondArticle")
        second_article = article_factory(
            title="second article popular",
            status=Article.StatusChoices.DRAFT,
            category=second_category,
            views=1000,
        )
        third_category = category_factory(name="forThirdArticle")
        third_article = article_factory(
            title="third article popular",
            status=Article.StatusChoices.DRAFT,
            category=third_category,
        )

        queryset = Article.objects.popular()

        assert queryset.first() == second_article

    def test_by_category_method(self, article_factory, category_factory):
        first_article = article_factory(
            title="first article by_category",
            status=Article.StatusChoices.PUBLISHED,
        )
        category = category_factory(name="forByCategory")
        second_article = article_factory(
            title="second article by_category",
            status=Article.StatusChoices.DRAFT,
            category=category,
        )
        third_article = article_factory(
            title="third article by_category",
            status=Article.StatusChoices.DRAFT,
            category=category,
        )

        queryset = Article.objects.by_category("forByCategory")

        assert set(queryset), {third_article, second_article}

    def test_by_slug(self, article_factory):
        article = article_factory(title="test by slug")

        queryset = Article.objects.by_slug("test-by-slug")
        assert queryset.slug == "test-by-slug"

        try:
            queryset = Article.objects.by_slug("test-not-exists")
        except Article.DoesNotExist:
            assert True

    def test_by_tag_method(self, article_factory, category_factory):
        first_article = article_factory(
            title="first article by_category",
            status=Article.StatusChoices.PUBLISHED,
            tags=["django"],
        )
        category = category_factory(name="forByCategory")
        second_article = article_factory(
            title="second article by_category",
            status=Article.StatusChoices.DRAFT,
            category=category,
            tags=["django", "flask"],
        )
        third_article = article_factory(
            title="third article by_category",
            status=Article.StatusChoices.DRAFT,
            category=category,
            tags=["flask"],
        )

        queryset = Article.objects.by_tag("flask")

        assert set(queryset) == {third_article, second_article}

        queryset = Article.objects.by_tag("django")

        assert set(queryset) == {first_article, second_article}


class TestCommentQueryset:
    def test_approved_method(self, comment_factory, category_factory, article_factory):
        category = category_factory(name="forApproved")
        article = article_factory(
            title="article approved",
            status=Article.StatusChoices.DRAFT,
            category=category,
        )
        approved_comment = comment_factory(is_approved=True, article=article)
        not_approved_comment = comment_factory(is_approved=False, article=article)

        queryset = Comment.objects.approved()

        assert queryset.first() == approved_comment

    def test_root_method(self, comment_factory, category_factory, article_factory):
        category = category_factory(name="forApproved")
        article = article_factory(
            title="article approved",
            status=Article.StatusChoices.DRAFT,
            category=category,
        )
        parent_comment = comment_factory(is_approved=True, article=article)
        sub_comment = comment_factory(
            is_approved=False,
            article=article,
            parent=parent_comment,
        )

        queryset = Comment.objects.root()

        assert queryset.first() == parent_comment

    def test_article_method(self, comment_factory, category_factory, article_factory):
        category = category_factory(name="forApproved")
        article = article_factory(
            title="article approved",
            status=Article.StatusChoices.DRAFT,
            category=category,
        )
        first_comment = comment_factory(
            is_approved=True,
            article=article,
        )
        second_comment = comment_factory(
            is_approved=False,
            article=article,
        )

        queryset = Comment.objects.for_article(article)

        assert set(queryset) == {first_comment, second_comment}

    def test_by_id_method(self, comment_factory, category_factory, article_factory):
        category = category_factory(name="forApproved")
        article = article_factory(
            title="article approved",
            status=Article.StatusChoices.DRAFT,
            category=category,
        )
        comment = comment_factory(
            is_approved=True,
            article=article,
        )

        queryset = Comment.objects.by_id(comment.id)

        assert queryset == comment
