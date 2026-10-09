import pytest
from apps.blog.models import Article, Comment
from apps.teammember_profile.services.profile_article_service import (
    ProfileArticleService,
)

from apps.teammember_profile.services.message_page_service import (
    MessagePageService,
)

from taggit.models import Tag
from apps.teammember_profile.services.public_teammember_service import (
    PublicTeamMemberService,
)

from django.core.paginator import Paginator
from apps.teammember_profile.services.profile_comments_service import (
    ProfileCommentsService,
)

from apps.teammember_profile.services.profile_articles_list_view_service import (
    ProfileArticlesListService,
)

from apps.teammember_profile.services.profile_dashboard_service import (
    ProfileDashboardService,
)

from apps.teammember_profile.services.profile_messages_service import (
    ProfileMessagesService,
)

pytestmark = pytest.mark.django_db


class TestMessagePageService:
    def test_init(self, user_factory):
        user = user_factory(
            is_superuser=False,
        )

        service = MessagePageService(user=user)

        assert service.user == user
        assert service.user_profile == user.profile

    def test_get_messages_when_user_is_none(self):
        service = MessagePageService.__new__(MessagePageService)
        service.user = None
        service.user_profile = None

        assert list(service.get_messages()) == []

    def test_get_messages_when_user_profile_is_none(self, user_factory):
        user = user_factory(
            is_superuser=False,
        )

        service = MessagePageService.__new__(MessagePageService)
        service.user = user
        service.user_profile = None

        assert list(service.get_messages()) == []

    def test_get_messages_for_regular_user(
        self,
        user_factory,
        profile_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        other_profile = profile_factory()

        own_message = message_factory(
            user_profile=user.profile,
        )
        other_message = message_factory(
            user_profile=other_profile,
        )
        public_message = message_factory(
            user_profile=None,
        )

        service = MessagePageService(user=user)

        assert set(service.get_messages()) == {
            own_message,
        }
        assert other_message not in service.get_messages()
        assert public_message not in service.get_messages()

    def test_get_messages_for_superuser(
        self,
        user_factory,
        profile_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=True,
        )
        other_profile = profile_factory()

        own_message = message_factory(
            user_profile=user.profile,
        )
        other_message = message_factory(
            user_profile=other_profile,
        )
        public_message = message_factory(
            user_profile=None,
        )

        service = MessagePageService(user=user)

        assert set(service.get_messages()) == {
            own_message,
            public_message,
        }
        assert other_message not in service.get_messages()

    def test_get_context(self, user_factory):
        user = user_factory(
            is_superuser=False,
        )

        service = MessagePageService(user=user)

        assert service.get_context(
            view_context={},
        ) == {
            "profile_instance": user.profile,
        }


class TestProfileArticleService:
    def test_init_without_article(self, user_factory):
        user = user_factory()

        service = ProfileArticleService(
            user_id=user.id,
        )

        assert service.user_profile == user.profile
        assert service.article is None
        assert service.article_model is Article

    def test_init_with_article(self, user_factory, article_factory):
        user = user_factory()
        article = article_factory(
            user_profile=user.profile,
        )

        service = ProfileArticleService(
            user_id=user.id,
            article_id=article.id,
        )

        assert service.user_profile == user.profile
        assert service.article == article
        assert service.article_model is Article

    def test_get_profile_by_user_id(self, user_factory):
        user = user_factory()

        profile = ProfileArticleService.get_profile_by_user_id(
            user_id=user.id,
        )

        assert profile == user.profile

    def test_get_profile_by_user_id_when_not_found(self):
        assert (
            ProfileArticleService.get_profile_by_user_id(
                user_id=999,
            )
            is None
        )

    def test_get_object_or_none_when_instance_id_is_none(self):
        assert (
            ProfileArticleService.get_object_or_none(
                model=Article,
                instance_id=None,
            )
            is None
        )

    def test_get_object_or_none_when_object_exists(
        self,
        article_factory,
    ):
        article = article_factory()

        result = ProfileArticleService.get_object_or_none(
            model=Article,
            instance_id=article.id,
        )

        assert result == article

    def test_get_object_or_none_when_object_does_not_exist(self):
        assert (
            ProfileArticleService.get_object_or_none(
                model=Article,
                instance_id=999,
            )
            is None
        )

    def test_get_context(self, user_factory):
        user = user_factory()

        service = ProfileArticleService(
            user_id=user.id,
        )

        assert service.get_context(
            view_context={},
        ) == {
            "profile_instance": user.profile,
        }

    def test_set_article(self, user_factory, article_factory):
        user = user_factory()
        article = article_factory()

        service = ProfileArticleService(
            user_id=user.id,
        )

        assert service.article is None

        service.set_article(article)

        assert service.article == article

    def test_get_article_queryset(
        self,
        user_factory,
        profile_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        own_article = article_factory(
            user_profile=user.profile,
        )

        other_profile = profile_factory()
        other_category = category_factory(
            user_profile=other_profile,
            name="other-category",
        )
        other_article = article_factory(
            user_profile=other_profile,
            category=other_category,
        )

        service = ProfileArticleService(
            user_id=user.id,
        )

        assert list(
            service.get_article_queryset(
                article_pk=own_article.id,
            )
        ) == [own_article]

        assert (
            list(
                service.get_article_queryset(
                    article_pk=other_article.id,
                )
            )
            == []
        )

    def test_get_article_queryset_when_article_does_not_exist(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileArticleService(
            user_id=user.id,
        )

        assert (
            list(
                service.get_article_queryset(
                    article_pk=999,
                )
            )
            == []
        )


class TestProfileArticlesListService:
    def test_init(self, user_factory):
        user = user_factory()

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert service.user == user
        assert service.user_profile == user.profile
        assert service.status == "all"
        assert service.article_model is Article
        assert service.search_query is None

    def test_init_with_search_query(self, user_factory):
        user = user_factory()

        service = ProfileArticlesListService(
            user=user,
            status="published",
            search_query="django",
        )

        assert service.status == "published"
        assert service.search_query == "django"

    def test_set_status_with_valid_status(self):
        assert ProfileArticlesListService.set_status("all") == "all"
        assert ProfileArticlesListService.set_status("published") == "published"
        assert ProfileArticlesListService.set_status("draft") == "draft"

    def test_set_status_with_uppercase_status(self):
        assert ProfileArticlesListService.set_status("ALL") == "all"
        assert ProfileArticlesListService.set_status("Published") == "published"
        assert ProfileArticlesListService.set_status("DRAFT") == "draft"

    def test_set_status_with_empty_value(self):
        assert ProfileArticlesListService.set_status(None) is None
        assert ProfileArticlesListService.set_status("") is None

    def test_set_status_with_non_string_value(self):
        assert ProfileArticlesListService.set_status(123) is None

    def test_set_status_with_invalid_status(self):
        assert ProfileArticlesListService.set_status("invalid") is None

    def test_get_articles_for_published_status(
        self,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="published-category",
        )

        published_article = article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
        )
        draft_article = article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.DRAFT,
        )
        deleted_article = article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
            is_deleted=True,
        )

        service = ProfileArticlesListService(
            user=user,
            status="published",
        )

        assert list(service.get_articles()) == [published_article]
        assert draft_article not in service.get_articles()
        assert deleted_article not in service.get_articles()

    def test_get_articles_for_draft_status(
        self,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="draft-category",
        )

        published_article = article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
        )
        draft_article = article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.DRAFT,
        )
        deleted_article = article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.DRAFT,
            is_deleted=True,
        )

        service = ProfileArticlesListService(
            user=user,
            status="draft",
        )

        assert list(service.get_articles()) == [draft_article]
        assert published_article not in service.get_articles()
        assert deleted_article not in service.get_articles()

    def test_get_articles_for_all_status(
        self,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="all-category",
        )

        published_article = article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
        )
        draft_article = article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.DRAFT,
        )
        deleted_article = article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
            is_deleted=True,
        )

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert set(service.get_articles()) == {
            published_article,
            draft_article,
        }
        assert deleted_article not in service.get_articles()

    def test_get_articles_filters_by_search_query(
        self,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="search-category",
        )

        matching_article = article_factory(
            user_profile=user.profile,
            category=category,
            title="Django Tutorial",
            excerpt="Learn Django step by step",
        )
        title_only_article = article_factory(
            user_profile=user.profile,
            category=category,
            title="Django Tutorial",
            excerpt="Learn Python step by step",
        )
        excerpt_only_article = article_factory(
            user_profile=user.profile,
            category=category,
            title="Python Tutorial",
            excerpt="Learn Django step by step",
        )

        service = ProfileArticlesListService(
            user=user,
            status="all",
            search_query="Django",
        )

        assert list(service.get_articles()) == [matching_article]
        assert title_only_article not in service.get_articles()
        assert excerpt_only_article not in service.get_articles()

    def test_get_articles_excludes_articles_from_other_profiles(
        self,
        user_factory,
        profile_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        other_profile = profile_factory()

        own_category = category_factory(
            user_profile=user.profile,
            name="own-category",
        )
        other_category = category_factory(
            user_profile=other_profile,
            name="other-category",
        )

        own_article = article_factory(
            user_profile=user.profile,
            category=own_category,
        )
        other_article = article_factory(
            user_profile=other_profile,
            category=other_category,
        )

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert list(service.get_articles()) == [own_article]
        assert other_article not in service.get_articles()

    def test_get_total_articles(
        self,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="total-category",
        )

        article_factory(
            user_profile=user.profile,
            category=category,
        )
        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.DRAFT,
        )

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert service._get_total_articles() == 2

    def test_get_total_articles_when_empty(self, user_factory):
        user = user_factory()

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert service._get_total_articles() == 0

    def test_get_total_published_articles(
        self,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="published-total-category",
        )

        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
        )
        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.DRAFT,
        )

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert service._get_total_published_articles() == 1

    def test_get_total_published_articles_when_empty(self, user_factory):
        user = user_factory()

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert service._get_total_published_articles() == 0

    def test_get_total_draft_articles(
        self,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="draft-total-category",
        )

        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.DRAFT,
        )
        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
        )

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert service._get_total_draft_articles() == 1

    def test_get_total_draft_articles_when_empty(self, user_factory):
        user = user_factory()

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert service._get_total_draft_articles() == 0

    def test_get_context_when_empty(self, user_factory):
        user = user_factory()

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        paginator = Paginator([], 3)
        page_obj = paginator.get_page(1)

        context = service.get_context(
            view_context={
                "paginator": paginator,
                "page_obj": page_obj,
            },
        )

        assert context["profile_instance"] == user.profile
        assert context["total_articles"] == 0
        assert context["total_published_articles"] == 0
        assert context["total_draft_articles"] == 0
        assert context["status"] == "all"
        assert list(context["custom_range"]) == list(
            paginator.get_elided_page_range(
                number=page_obj.number,
                on_each_side=2,
                on_ends=1,
            )
        )

    def test_get_context_with_articles(
        self,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="context-category",
        )

        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
        )
        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.DRAFT,
        )

        service = ProfileArticlesListService(
            user=user,
            status="draft",
        )

        articles = list(
            Article.objects.filter(
                user_profile=user.profile,
            )
        )
        paginator = Paginator(articles, 1)
        page_obj = paginator.get_page(1)

        context = service.get_context(
            view_context={
                "paginator": paginator,
                "page_obj": page_obj,
            },
        )

        assert context["profile_instance"] == user.profile
        assert context["total_articles"] == 2
        assert context["total_published_articles"] == 1
        assert context["total_draft_articles"] == 1
        assert context["status"] == "draft"
        assert list(context["custom_range"]) == list(
            paginator.get_elided_page_range(
                number=page_obj.number,
                on_each_side=2,
                on_ends=1,
            )
        )

    def test_delete_article_when_article_does_not_exist(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert service.delete_article(999) is False

    def test_delete_article_when_article_belongs_to_another_profile(
        self,
        user_factory,
        profile_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        other_profile = profile_factory()

        other_category = category_factory(
            user_profile=other_profile,
            name="delete-other-category",
        )
        other_article = article_factory(
            user_profile=other_profile,
            category=other_category,
        )

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert service.delete_article(other_article.id) is False

        other_article.refresh_from_db()
        assert other_article.is_deleted is False

    def test_delete_article_when_already_deleted(
        self,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="already-deleted-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
            is_deleted=True,
        )

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert service.delete_article(article.id) is True

        article.refresh_from_db()
        assert article.is_deleted is True

    def test_delete_article_success(
        self,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="delete-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
            is_deleted=False,
        )

        service = ProfileArticlesListService(
            user=user,
            status="all",
        )

        assert service.delete_article(article.id) is True

        article.refresh_from_db()

        assert article.is_deleted is True
        assert article.deleted_at is not None


class TestProfileCommentsService:
    def test_init(self, user_factory):
        user = user_factory()

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.user == user
        assert service.user_profile == user.profile
        assert service.status == "all"
        assert service.search_query is None
        assert service.comment_model.__name__ == "Comment"

    def test_init_with_search_query(self, user_factory):
        user = user_factory()

        service = ProfileCommentsService(
            user=user,
            status="approved",
            search_query="  django  ",
        )

        assert service.status == "approved"
        assert service.search_query == "django"

    def test_set_status_with_valid_values(self):
        assert ProfileCommentsService._set_status("all") == "all"
        assert ProfileCommentsService._set_status("approved") == "approved"
        assert ProfileCommentsService._set_status("pending") == "pending"

    def test_set_status_with_uppercase_value(self):
        assert ProfileCommentsService._set_status("ALL") == "all"
        assert ProfileCommentsService._set_status("Approved") == "approved"
        assert ProfileCommentsService._set_status("PENDING") == "pending"

    def test_set_status_with_empty_value(self):
        assert ProfileCommentsService._set_status(None) is None
        assert ProfileCommentsService._set_status("") is None

    def test_set_status_with_non_string_value(self):
        assert ProfileCommentsService._set_status(123) is None

    def test_set_status_with_invalid_value(self):
        assert ProfileCommentsService._set_status("invalid") is None

    def test_set_search_query_with_valid_value(self):
        assert (
            ProfileCommentsService._set_search_query(
                "django",
            )
            == "django"
        )

    def test_set_search_query_strips_whitespace(self):
        assert (
            ProfileCommentsService._set_search_query(
                "  django  ",
            )
            == "django"
        )

    def test_set_search_query_with_empty_value(self):
        assert ProfileCommentsService._set_search_query(None) is None
        assert ProfileCommentsService._set_search_query("") is None
        assert ProfileCommentsService._set_search_query("   ") is None

    def test_set_search_query_with_non_string_value(self):
        assert ProfileCommentsService._set_search_query(123) is None

    def test_get_comments_for_all_status(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="comments-all-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        approved_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )
        pending_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )
        deleted_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_deleted=True,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert set(service.get_comments()) == {
            approved_comment,
            pending_comment,
        }
        assert deleted_comment not in service.get_comments()

    def test_get_comments_for_approved_status(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="comments-approved-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        approved_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )
        pending_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )

        service = ProfileCommentsService(
            user=user,
            status="approved",
        )

        assert list(service.get_comments()) == [approved_comment]
        assert pending_comment not in service.get_comments()

    def test_get_comments_for_pending_status(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="comments-pending-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        approved_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )
        pending_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )

        service = ProfileCommentsService(
            user=user,
            status="pending",
        )

        assert list(service.get_comments()) == [pending_comment]
        assert approved_comment not in service.get_comments()

    def test_get_comments_for_other_profile(
        self,
        user_factory,
        profile_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        other_profile = profile_factory()

        own_category = category_factory(
            user_profile=user.profile,
            name="comments-own-category",
        )
        other_category = category_factory(
            user_profile=other_profile,
            name="comments-other-category",
        )

        own_article = article_factory(
            user_profile=user.profile,
            category=own_category,
        )
        other_article = article_factory(
            user_profile=other_profile,
            category=other_category,
        )

        own_comment = comment_factory(
            user_profile=user.profile,
            article=own_article,
        )
        other_comment = comment_factory(
            user_profile=other_profile,
            article=other_article,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert list(service.get_comments()) == [own_comment]
        assert other_comment not in service.get_comments()

    def test_get_comments_searches_by_name(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="comments-search-name-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
            title="Normal article title",
        )

        matching_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            name="needle name",
        )
        other_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            name="another name",
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
            search_query="needle",
        )

        assert list(service.get_comments()) == [matching_comment]
        assert other_comment not in service.get_comments()

    def test_get_comments_searches_by_email(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="comments-search-email-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        matching_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            email="needle@example.com",
        )
        other_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            email="other@example.com",
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
            search_query="needle",
        )

        assert list(service.get_comments()) == [matching_comment]
        assert other_comment not in service.get_comments()

    def test_get_comments_searches_by_body(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="comments-search-body-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        matching_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            body="This body contains needle",
        )
        other_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            body="This body does not match",
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
            search_query="needle",
        )

        assert list(service.get_comments()) == [matching_comment]
        assert other_comment not in service.get_comments()

    def test_get_comments_searches_by_article_title(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="comments-search-title-category",
        )

        matching_article = article_factory(
            user_profile=user.profile,
            category=category,
            title="Article with needle",
        )
        other_article = article_factory(
            user_profile=user.profile,
            category=category,
            title="Another article",
        )

        matching_comment = comment_factory(
            user_profile=user.profile,
            article=matching_article,
        )
        other_comment = comment_factory(
            user_profile=user.profile,
            article=other_article,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
            search_query="needle",
        )

        assert list(service.get_comments()) == [matching_comment]
        assert other_comment not in service.get_comments()

    def test_get_total_comments(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="comments-total-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        first_comment = comment_factory(
            user_profile=user.profile,
            article=article,
        )
        second_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )
        comment_factory(
            user_profile=user.profile,
            article=article,
            parent=first_comment,
        )
        comment_factory(
            user_profile=user.profile,
            article=article,
            is_deleted=True,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service._get_total_comments() == 2

    def test_get_total_approved_comments(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="comments-approved-total-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )
        comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service._get_total_approved_comments() == 1

    def test_get_total_pending_comments(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="comments-pending-total-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )
        comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service._get_total_pending_comments() == 1

    def test_get_context(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="comments-context-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )
        comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )

        service = ProfileCommentsService(
            user=user,
            status="approved",
            search_query="  test  ",
        )

        paginator = Paginator([1, 2, 3, 4, 5], 2)
        page_obj = paginator.get_page(2)

        context = service.get_context(
            view_context={
                "paginator": paginator,
                "page_obj": page_obj,
            },
        )

        assert context["profile_instance"] == user.profile
        assert context["status"] == "approved"
        assert context["search_query"] == "test"
        assert context["total_comments"] == 1
        assert context["total_approved_comments"] == 1
        assert context["total_pending_comments"] == 0
        assert list(context["custom_range"]) == list(
            paginator.get_elided_page_range(
                number=page_obj.number,
                on_each_side=2,
                on_ends=1,
            )
        )

    def test_get_active_replies_prefetch(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="comments-prefetch-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        parent_comment = comment_factory(
            user_profile=user.profile,
            article=article,
        )
        active_reply = comment_factory(
            user_profile=user.profile,
            article=article,
            parent=parent_comment,
            is_deleted=False,
        )
        deleted_reply = comment_factory(
            user_profile=user.profile,
            article=article,
            parent=parent_comment,
            is_deleted=True,
        )
        comment_factory(
            user_profile=user.profile,
            article=article,
            parent=active_reply,
            is_deleted=False,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        comments = list(service.get_comments())
        comment = comments[0]

        assert comment == parent_comment
        assert comment.active_sub_comments == [active_reply]
        assert deleted_reply not in comment.active_sub_comments

    def test_accept_comment_when_not_found(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.accept_comment(999) is False

    def test_accept_comment_when_belongs_to_other_profile(
        self,
        user_factory,
        profile_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        other_profile = profile_factory()

        category = category_factory(
            user_profile=other_profile,
            name="accept-other-category",
        )
        article = article_factory(
            user_profile=other_profile,
            category=category,
        )
        comment = comment_factory(
            user_profile=other_profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.accept_comment(comment.id) is False

    def test_accept_comment_when_already_approved(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="accept-approved-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )
        comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )
        approved_at = comment.approved_at

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.accept_comment(comment.id) is True

        comment.refresh_from_db()

        assert comment.is_approved is True
        assert comment.approved_at == approved_at

    def test_accept_comment_success(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="accept-success-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )
        comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.accept_comment(comment.id) is True

        comment.refresh_from_db()

        assert comment.is_approved is True
        assert comment.approved_at is not None

    def test_accept_comment_when_deleted(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="accept-deleted-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )
        comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_deleted=True,
            is_approved=False,
            approved_at=None,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.accept_comment(comment.id) is False

    def test_reject_comment_when_not_found(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.reject_comment(999) is False

    def test_reject_comment_when_already_pending(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="reject-pending-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )
        comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.reject_comment(comment.id) is True

        comment.refresh_from_db()

        assert comment.is_approved is False
        assert comment.approved_at is None

    def test_reject_comment_success(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="reject-success-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )
        comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.reject_comment(comment.id) is True

        comment.refresh_from_db()

        assert comment.is_approved is False
        assert comment.approved_at is None

    def test_reject_comment_when_deleted(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="reject-deleted-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )
        comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_deleted=True,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.reject_comment(comment.id) is False

    def test_delete_comment_when_not_found(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.delete_comment(999) is False

    def test_delete_comment_when_belongs_to_other_profile(
        self,
        user_factory,
        profile_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        other_profile = profile_factory()

        category = category_factory(
            user_profile=other_profile,
            name="delete-other-category",
        )
        article = article_factory(
            user_profile=other_profile,
            category=category,
        )
        comment = comment_factory(
            user_profile=other_profile,
            article=article,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.delete_comment(comment.id) is False

        comment.refresh_from_db()

        assert comment.is_deleted is False

    def test_delete_comment_when_already_deleted(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="delete-already-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )
        comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_deleted=True,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.delete_comment(comment.id) is True

        comment.refresh_from_db()

        assert comment.is_deleted is True

    def test_delete_comment_success(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="delete-success-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )
        comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_deleted=False,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert service.delete_comment(comment.id) is True

        comment.refresh_from_db()

        assert comment.is_deleted is True
        assert comment.deleted_at is not None

    def test_reply_comment_when_body_is_empty(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert (
            service.reply_comment(
                parent_id=999,
                body="   ",
            )
            is False
        )

    def test_reply_comment_when_parent_does_not_exist(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert (
            service.reply_comment(
                parent_id=999,
                body="test reply",
            )
            is False
        )

    def test_reply_comment_when_parent_is_not_approved(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="reply-pending-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )
        parent_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert (
            service.reply_comment(
                parent_id=parent_comment.id,
                body="test reply",
            )
            is False
        )

    def test_reply_comment_when_parent_is_second_level_reply(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="reply-second-level-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        top_level_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )
        first_level_reply = comment_factory(
            user_profile=user.profile,
            article=article,
            parent=top_level_comment,
            is_approved=True,
        )
        second_level_reply = comment_factory(
            user_profile=user.profile,
            article=article,
            parent=first_level_reply,
            is_approved=True,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert (
            service.reply_comment(
                parent_id=second_level_reply.id,
                body="test reply",
            )
            is False
        )

    def test_reply_comment_success(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="reply-success-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )
        parent_comment = comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )

        service = ProfileCommentsService(
            user=user,
            status="all",
        )

        assert (
            service.reply_comment(
                parent_id=parent_comment.id,
                body="  test reply  ",
            )
            is True
        )

        reply = parent_comment.sub_comments.get()

        assert reply.user_profile == user.profile
        assert reply.article == article
        assert reply.parent == parent_comment
        assert reply.name == user.profile.full_name
        assert reply.email == user.profile.email
        assert reply.body == "test reply"
        assert reply.is_approved is False
        assert reply.approved_at is None


class TestProfileDashboardService:
    def test_init(self, user_factory):
        user = user_factory()

        service = ProfileDashboardService(user=user)

        assert service.user == user
        assert service.user_profile == user.profile
        assert service.article_model is Article
        assert service.comment_model is Comment
        assert isinstance(
            service.message_service,
            MessagePageService,
        )

    def test_get_profile(self, user_factory):
        user = user_factory()

        service = ProfileDashboardService(user=user)

        assert service.get_profile(user.profile.id) == user.profile
        assert service.get_profile(999) is None

    def test_get_recent_articles(
        self,
        user_factory,
        article_factory,
        category_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="dashboard-recent-category",
        )

        recent_articles = article_factory.create_batch(
            4,
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
        )

        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.DRAFT,
        )

        other_profile_article = article_factory(
            category=category,
            status=Article.StatusChoices.PUBLISHED,
        )

        service = ProfileDashboardService(user=user)

        assert set(service._get_recent_articles()) == set(recent_articles)
        assert other_profile_article not in service._get_recent_articles()

    def test_get_latest_messages(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory()

        latest_messages = message_factory.create_batch(
            3,
            user_profile=user.profile,
            is_read=False,
        )
        message_factory(
            user_profile=user.profile,
            is_read=True,
        )

        service = ProfileDashboardService(user=user)

        assert set(service._get_latest_messages()) == set(latest_messages)

    def test_get_latest_messages_when_message_service_is_none(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileDashboardService(user=user)
        service.message_service = None

        assert service._get_latest_messages() is None

    def test_get_latest_comments(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="dashboard-latest-comments-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        latest_comments = comment_factory.create_batch(
            3,
            user_profile=user.profile,
            article=article,
        )

        assert len(latest_comments) == 3

        service = ProfileDashboardService(user=user)

        assert set(service._get_latest_comments()) == set(latest_comments)

    def test_get_total_views(
        self,
        user_factory,
        article_factory,
        category_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="dashboard-views-category",
        )

        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
            views=1000,
        )
        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
            views=2500,
        )
        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.DRAFT,
            views=5000,
        )

        service = ProfileDashboardService(user=user)

        assert service._get_total_views() == 3.5

    def test_get_total_views_when_no_published_articles(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileDashboardService(user=user)

        assert service._get_total_views() == 0

    def test_get_total_comments(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="dashboard-total-comments-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )
        comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )

        service = ProfileDashboardService(user=user)

        assert service._get_total_comments() == 1

    def test_get_total_comments_when_empty(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileDashboardService(user=user)

        assert service._get_total_comments() == 0

    def test_get_total_pending_comment(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="dashboard-pending-comments-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
        )

        comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )
        comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )

        service = ProfileDashboardService(user=user)

        assert service._get_total_pending_comment() == 2

    def test_get_total_pending_comment_when_empty(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileDashboardService(user=user)

        assert service._get_total_pending_comment() == 0

    def test_get_total_articles(
        self,
        user_factory,
        article_factory,
        category_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="dashboard-total-articles-category",
        )

        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
        )
        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
        )
        article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.DRAFT,
        )

        service = ProfileDashboardService(user=user)

        assert service._get_total_articles() == 2

    def test_get_total_articles_when_empty(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileDashboardService(user=user)

        assert service._get_total_articles() == 0

    def test_get_total_messages(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory()

        message_factory(
            user_profile=user.profile,
            is_read=True,
        )
        message_factory(
            user_profile=user.profile,
            is_read=False,
        )

        service = ProfileDashboardService(user=user)

        assert service._get_total_messages() == 2

    def test_get_total_messages_when_message_service_is_none(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileDashboardService(user=user)
        service.message_service = None

        assert service._get_total_messages() == 0

    def test_get_total_unread_messages(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory()

        message_factory(
            user_profile=user.profile,
            is_read=False,
        )
        message_factory(
            user_profile=user.profile,
            is_read=False,
        )
        message_factory(
            user_profile=user.profile,
            is_read=True,
        )

        service = ProfileDashboardService(user=user)

        assert service._get_total_unread_messages() == 2

    def test_get_total_unread_messages_when_message_service_is_none(
        self,
        user_factory,
    ):
        user = user_factory()

        service = ProfileDashboardService(user=user)
        service.message_service = None

        assert service._get_total_unread_messages() == 0

    def test_get_context(
        self,
        user_factory,
        article_factory,
        category_factory,
        comment_factory,
        message_factory,
    ):
        user = user_factory()
        category = category_factory(
            user_profile=user.profile,
            name="dashboard-context-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
            status=Article.StatusChoices.PUBLISHED,
            views=1500,
        )

        comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=True,
        )
        comment_factory(
            user_profile=user.profile,
            article=article,
            is_approved=False,
            approved_at=None,
        )

        message_factory(
            user_profile=user.profile,
            is_read=False,
        )
        message_factory(
            user_profile=user.profile,
            is_read=True,
        )

        service = ProfileDashboardService(user=user)

        context = service.get_context(
            view_context={},
        )

        assert context["profile_instance"] == user.profile
        assert context["total_articles"] == 1
        assert context["total_views"] == 1.5
        assert context["total_comments"] == 1
        assert context["total_messages"] == 2
        assert context["total_pending_comments"] == 2
        assert context["total_unread_messages"] == 1
        assert list(context["recent_articles"]) == [article]
        assert len(context["latest_messages"]) == 1
        assert context["latest_comments"].count() == 2


class TestProfileMessagesService:
    def test_init(self, user_factory):
        user = user_factory(
            is_superuser=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.user == user
        assert service.user_profile == user.profile
        assert service.status == "inbox"
        assert service.search_query is None

    def test_init_with_search_query(self, user_factory):
        user = user_factory(
            is_superuser=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="sent",
            search_query="django",
        )

        assert service.status == "sent"
        assert service.search_query == "django"

    def test_set_profile_with_valid_values(self):
        assert ProfileMessagesService._set_profile("inbox") == "inbox"
        assert ProfileMessagesService._set_profile("sent") == "sent"
        assert ProfileMessagesService._set_profile("archived") == "archived"
        assert ProfileMessagesService._set_profile("read") == "read"

    def test_set_profile_with_uppercase_values(self):
        assert ProfileMessagesService._set_profile("INBOX") == "inbox"
        assert ProfileMessagesService._set_profile("Sent") == "sent"
        assert ProfileMessagesService._set_profile("ARCHIVED") == "archived"
        assert ProfileMessagesService._set_profile("Read") == "read"

    def test_set_profile_with_empty_value(self):
        assert ProfileMessagesService._set_profile(None) is None
        assert ProfileMessagesService._set_profile("") is None

    def test_set_profile_with_non_string_value(self):
        assert ProfileMessagesService._set_profile(123) is None

    def test_set_profile_with_invalid_value(self):
        assert ProfileMessagesService._set_profile("invalid") is None

    def test_set_query_set_with_valid_value(self):
        assert ProfileMessagesService._set_query_set("django") == "django"

    def test_set_query_set_preserves_whitespace(self):
        assert ProfileMessagesService._set_query_set("  django  ") == "  django  "

    def test_set_query_set_with_empty_value(self):
        assert ProfileMessagesService._set_query_set(None) is None
        assert ProfileMessagesService._set_query_set("") is None

    def test_set_query_set_with_non_string_value(self):
        assert ProfileMessagesService._set_query_set(123) is None

    def test_get_messages_for_inbox(
        self,
        user_factory,
        profile_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        other_profile = profile_factory()

        own_message = message_factory(
            user_profile=user.profile,
        )
        own_reply = message_factory(
            user_profile=user.profile,
            parent=own_message,
        )
        other_message = message_factory(
            user_profile=other_profile,
        )
        public_message = message_factory(
            user_profile=None,
        )
        deleted_message = message_factory(
            user_profile=user.profile,
            is_deleted=True,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert set(service.get_messages()) == {
            own_message,
            own_reply,
        }
        assert other_message not in service.get_messages()
        assert public_message not in service.get_messages()
        assert deleted_message not in service.get_messages()

    def test_get_messages_for_sent(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )

        sent_message = message_factory(
            user_profile=user.profile,
            parent=None,
        )
        message_factory(
            user_profile=user.profile,
            parent=sent_message,
        )

        service = ProfileMessagesService(
            user=user,
            status="sent",
        )

        assert list(service.get_messages()) == [sent_message]

    def test_get_messages_for_archived(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )

        archived_message = message_factory(
            user_profile=user.profile,
            is_archived=True,
        )
        message_factory(
            user_profile=user.profile,
            is_archived=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="archived",
        )

        assert list(service.get_messages()) == [archived_message]

    def test_get_messages_for_read(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )

        read_message = message_factory(
            user_profile=user.profile,
            is_read=True,
        )
        message_factory(
            user_profile=user.profile,
            is_read=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="read",
        )

        assert list(service.get_messages()) == [read_message]

    def test_get_messages_for_superuser(
        self,
        user_factory,
        profile_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=True,
        )
        other_profile = profile_factory()

        own_message = message_factory(
            user_profile=user.profile,
        )
        public_message = message_factory(
            user_profile=None,
        )
        other_message = message_factory(
            user_profile=other_profile,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert set(service.get_messages()) == {
            own_message,
            public_message,
        }
        assert other_message not in service.get_messages()

    def test_get_messages_searches_by_name_email_subject_and_body(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )

        name_message = message_factory(
            user_profile=user.profile,
            name="needle name",
            email="name@example.com",
            subject="Ordinary subject",
            body="Ordinary body",
        )
        email_message = message_factory(
            user_profile=user.profile,
            name="Another name",
            email="needle@example.com",
            subject="Ordinary subject",
            body="Ordinary body",
        )
        subject_message = message_factory(
            user_profile=user.profile,
            name="Another name",
            email="subject@example.com",
            subject="needle subject",
            body="Ordinary body",
        )
        body_message = message_factory(
            user_profile=user.profile,
            name="Another name",
            email="body@example.com",
            subject="Ordinary subject",
            body="needle body",
        )
        other_message = message_factory(
            user_profile=user.profile,
            name="Another name",
            email="other@example.com",
            subject="Different subject",
            body="Different body",
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
            search_query="needle",
        )

        assert set(service.get_messages()) == {
            name_message,
            email_message,
            subject_message,
            body_message,
        }
        assert other_message not in service.get_messages()

    def test_total_unread_messages_for_regular_user(
        self,
        user_factory,
        profile_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        other_profile = profile_factory()

        message_factory(
            user_profile=user.profile,
            is_read=False,
        )
        message_factory(
            user_profile=user.profile,
            is_read=False,
        )
        message_factory(
            user_profile=user.profile,
            is_read=True,
        )
        message_factory(
            user_profile=user.profile,
            is_read=False,
            is_deleted=True,
        )
        message_factory(
            user_profile=other_profile,
            is_read=False,
        )
        message_factory(
            user_profile=None,
            is_read=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.total_unread_messages() == 2

    def test_total_unread_messages_for_superuser(
        self,
        user_factory,
        profile_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=True,
        )
        other_profile = profile_factory()

        message_factory(
            user_profile=user.profile,
            is_read=False,
        )
        message_factory(
            user_profile=None,
            is_read=False,
        )
        message_factory(
            user_profile=other_profile,
            is_read=False,
        )
        message_factory(
            user_profile=user.profile,
            is_read=True,
        )
        message_factory(
            user_profile=None,
            is_read=False,
            is_deleted=True,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.total_unread_messages() == 2

    def test_get_context(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )

        message_factory(
            user_profile=user.profile,
            is_read=False,
        )
        message_factory(
            user_profile=user.profile,
            is_read=True,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        paginator = Paginator([1, 2, 3, 4, 5], 2)
        page_obj = paginator.get_page(2)

        context = service.get_context(
            view_context={
                "paginator": paginator,
                "page_obj": page_obj,
            },
        )

        assert context["profile_instance"] == user.profile
        assert context["status"] == "inbox"
        assert context["total_unread_messages"] == 1
        assert list(context["custom_range"]) == list(
            paginator.get_elided_page_range(
                number=page_obj.number,
                on_each_side=2,
                on_ends=1,
            )
        )

    def test_set_all_messages_as_read_for_regular_user(
        self,
        user_factory,
        profile_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        other_profile = profile_factory()

        unread_message = message_factory(
            user_profile=user.profile,
            is_read=False,
        )
        read_message = message_factory(
            user_profile=user.profile,
            is_read=True,
        )
        deleted_message = message_factory(
            user_profile=user.profile,
            is_read=False,
            is_deleted=True,
        )
        other_message = message_factory(
            user_profile=other_profile,
            is_read=False,
        )
        public_message = message_factory(
            user_profile=None,
            is_read=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.set_all_messages_as_read() is True

        unread_message.refresh_from_db()
        read_message.refresh_from_db()
        deleted_message.refresh_from_db()
        other_message.refresh_from_db()
        public_message.refresh_from_db()

        assert unread_message.is_read is True
        assert read_message.is_read is True
        assert deleted_message.is_read is False
        assert other_message.is_read is False
        assert public_message.is_read is False

    def test_set_all_messages_as_read_for_superuser(
        self,
        user_factory,
        profile_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=True,
        )
        other_profile = profile_factory()

        own_message = message_factory(
            user_profile=user.profile,
            is_read=False,
        )
        public_message = message_factory(
            user_profile=None,
            is_read=False,
        )
        other_message = message_factory(
            user_profile=other_profile,
            is_read=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.set_all_messages_as_read() is True

        own_message.refresh_from_db()
        public_message.refresh_from_db()
        other_message.refresh_from_db()

        assert own_message.is_read is True
        assert public_message.is_read is True
        assert other_message.is_read is False

    def test_delete_message_success(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        message = message_factory(
            user_profile=user.profile,
            is_deleted=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.delete_message(message.id) is True

        message.refresh_from_db()

        assert message.is_deleted is True

    def test_delete_message_when_not_found(self, user_factory):
        user = user_factory(
            is_superuser=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.delete_message(999) is False

    def test_delete_message_forbidden_for_other_profile_or_public_message(
        self,
        user_factory,
        profile_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        other_profile = profile_factory()

        other_message = message_factory(
            user_profile=other_profile,
        )
        public_message = message_factory(
            user_profile=None,
        )
        deleted_message = message_factory(
            user_profile=user.profile,
            is_deleted=True,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.delete_message(other_message.id) is False
        assert service.delete_message(public_message.id) is False
        assert service.delete_message(deleted_message.id) is False

    def test_delete_public_message_for_superuser(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=True,
        )
        message = message_factory(
            user_profile=None,
            is_deleted=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.delete_message(message.id) is True

        message.refresh_from_db()

        assert message.is_deleted is True

    def test_archive_message_success(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        message = message_factory(
            user_profile=user.profile,
            is_deleted=False,
            is_archived=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.archive_message(message.id) is True

        message.refresh_from_db()

        assert message.is_archived is True

    def test_archive_message_when_not_found(self, user_factory):
        user = user_factory(
            is_superuser=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.archive_message(999) is False

    def test_archive_message_forbidden_for_other_profile_or_public_message(
        self,
        user_factory,
        profile_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        other_profile = profile_factory()

        other_message = message_factory(
            user_profile=other_profile,
            is_archived=False,
        )
        public_message = message_factory(
            user_profile=None,
            is_archived=False,
        )
        archived_message = message_factory(
            user_profile=user.profile,
            is_archived=True,
        )
        deleted_message = message_factory(
            user_profile=user.profile,
            is_archived=False,
            is_deleted=True,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.archive_message(other_message.id) is False
        assert service.archive_message(public_message.id) is False
        assert service.archive_message(archived_message.id) is False
        assert service.archive_message(deleted_message.id) is False

    def test_archive_public_message_for_superuser(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=True,
        )
        message = message_factory(
            user_profile=None,
            is_deleted=False,
            is_archived=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert service.archive_message(message.id) is True

        message.refresh_from_db()

        assert message.is_archived is True

    def test_reply_message_success(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        parent_message = message_factory(
            user_profile=user.profile,
            is_deleted=False,
            subject="Original subject",
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert (
            service.reply_message(
                message_id=parent_message.id,
                reply_body="This is a reply",
            )
            is True
        )

        reply = service.message_model.objects.get(
            user_profile=user.profile,
            parent=parent_message,
        )

        assert reply.user_profile == user.profile
        assert reply.parent == parent_message
        assert reply.name == user.profile.full_name
        assert reply.email == user.profile.email
        assert reply.subject == "Reply to your message: Original subject"
        assert reply.body == "This is a reply"

    def test_reply_message_when_not_found(self, user_factory):
        user = user_factory(
            is_superuser=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert (
            service.reply_message(
                message_id=999,
                reply_body="This is a reply",
            )
            is False
        )

    def test_reply_message_forbidden_for_other_profile(
        self,
        user_factory,
        profile_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        other_profile = profile_factory()

        other_message = message_factory(
            user_profile=other_profile,
            is_deleted=False,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert (
            service.reply_message(
                message_id=other_message.id,
                reply_body="This is a reply",
            )
            is False
        )

    def test_reply_message_when_message_is_deleted(
        self,
        user_factory,
        message_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        message = message_factory(
            user_profile=user.profile,
            is_deleted=True,
        )

        service = ProfileMessagesService(
            user=user,
            status="inbox",
        )

        assert (
            service.reply_message(
                message_id=message.id,
                reply_body="This is a reply",
            )
            is False
        )


class TestPublicTeamMemberService:
    def test_init(self, user_factory):
        user = user_factory(
            is_superuser=False,
        )

        service = PublicTeamMemberService(user=user)

        assert service.user == user
        assert service.user_profile == user.profile

    def test_get_articles(
        self,
        user_factory,
        profile_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        own_category = category_factory(
            user_profile=user.profile,
            name="public-own-category",
        )
        other_profile = profile_factory()
        other_category = category_factory(
            user_profile=other_profile,
            name="public-other-category",
        )

        published_article = article_factory(
            user_profile=user.profile,
            category=own_category,
            title="Public published article",
            status=Article.StatusChoices.PUBLISHED,
        )
        article_factory(
            user_profile=user.profile,
            category=own_category,
            title="Public draft article",
            status=Article.StatusChoices.DRAFT,
        )
        other_article = article_factory(
            user_profile=other_profile,
            category=other_category,
            title="Other profile article",
            status=Article.StatusChoices.PUBLISHED,
        )

        service = PublicTeamMemberService(user=user)

        assert list(service.get_articles()) == [published_article]
        assert other_article not in service.get_articles()

    def test_get_context(
        self,
        user_factory,
        category_factory,
        article_factory,
        comment_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        category = category_factory(
            user_profile=user.profile,
            name="public-context-category",
        )

        published_articles = [
            article_factory(
                user_profile=user.profile,
                category=category,
                title=f"Public context article {index}",
                status=Article.StatusChoices.PUBLISHED,
                views=1250,
            )
            for index in range(5)
        ]

        article_factory(
            user_profile=user.profile,
            category=category,
            title="Public context draft",
            status=Article.StatusChoices.DRAFT,
            views=10000,
        )

        comment_factory(
            user_profile=user.profile,
            article=published_articles[0],
            is_approved=True,
        )
        comment_factory(
            user_profile=user.profile,
            article=published_articles[1],
            is_approved=True,
        )
        comment_factory(
            user_profile=user.profile,
            article=published_articles[2],
            is_approved=False,
            approved_at=None,
        )

        tag_names = [f"public-team-member-tag-{index}" for index in range(12)]
        for tag_name in tag_names:
            Tag.objects.create(
                name=tag_name,
                slug=tag_name,
            )

        service = PublicTeamMemberService(user=user)

        paginator = Paginator(list(range(20)), 2)
        page_obj = paginator.get_page(5)

        context = service.get_context(
            view_context={
                "paginator": paginator,
                "page_obj": page_obj,
            },
        )

        assert context["profile_instance"] == user.profile
        assert context["total_views"] == 6
        assert context["total_comments"] == 2

        assert len(context["tags"]) == 10
        assert all(tag.name in tag_names for tag in context["tags"])

        assert len(context["recent_posts"]) == 4
        assert set(context["recent_posts"]).issubset(
            set(published_articles),
        )

        assert list(context["custom_range"]) == list(
            paginator.get_elided_page_range(
                number=page_obj.number,
                on_each_side=2,
                on_ends=1,
            )
        )

    def test_get_context_when_total_views_is_zero(
        self,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory(
            is_superuser=False,
        )
        category = category_factory(
            user_profile=user.profile,
            name="public-zero-views-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
            title="Public zero views article",
            status=Article.StatusChoices.PUBLISHED,
            views=0,
        )

        service = PublicTeamMemberService(user=user)

        paginator = Paginator([1, 2, 3], 2)
        page_obj = paginator.get_page(1)

        context = service.get_context(
            view_context={
                "paginator": paginator,
                "page_obj": page_obj,
            },
        )

        assert context["profile_instance"] == user.profile
        assert context["total_views"] == 0
        assert context["total_comments"] == 0
        assert list(context["recent_posts"]) == [article]
