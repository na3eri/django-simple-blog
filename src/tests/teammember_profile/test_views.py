from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import Http404, HttpResponse

from apps.blog.models import Article, Comment, Message
from apps.teammember_profile import views


pytestmark = pytest.mark.django_db


def make_request(rf, user, method="get", path="/", data=None):
    if method.lower() == "post":
        request = rf.post(path, data=data or {})
    else:
        request = rf.get(path, data=data or {})

    request.user = user

    SessionMiddleware(lambda request: None).process_request(request)
    request._messages = FallbackStorage(request)

    return request


def get_message_texts(request):
    return [str(message) for message in get_messages(request)]


def install_service(monkeypatch, service_name, service):
    constructor = Mock(return_value=service)
    monkeypatch.setattr(views, service_name, constructor)
    return constructor


class TestTeamMemberPublicView:
    def test_get_articles_and_context(
        self,
        rf,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory(is_superuser=False)
        category = category_factory(
            user_profile=user.profile,
            name="public-view-category",
        )

        articles = [
            article_factory(
                user_profile=user.profile,
                category=category,
                title=f"Public article {index}",
                status=Article.StatusChoices.PUBLISHED,
            )
            for index in range(5)
        ]

        request = make_request(rf, user)
        response = views.TeamMemberPublicView.as_view()(request)

        assert response.status_code == 200
        assert "teammember_profile/team-member.html" in response.template_name
        assert response.context_data["profile_instance"] == user.profile
        assert response.context_data["paginator"].count == 5
        assert response.context_data["is_paginated"] is True
        assert len(response.context_data["articles"]) == 4
        assert set(response.context_data["articles"]).issubset(set(articles))

    def test_get_queryset_uses_service(
        self,
        rf,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory(is_superuser=False)
        category = category_factory(
            user_profile=user.profile,
            name="public-queryset-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
            title="Public queryset article",
            status=Article.StatusChoices.PUBLISHED,
        )

        request = make_request(rf, user)
        response = views.TeamMemberPublicView.as_view()(request)

        assert article in response.context_data["articles"]

    def test_setup_raises_404_without_profile(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(user_profile=None)
        install_service(monkeypatch, "PublicTeamMemberService", service)

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.TeamMemberPublicView.as_view()(request)


class TestMessageView:
    def test_get_context(self, rf, user_factory):
        user = user_factory(is_superuser=False)
        request = make_request(rf, user)

        response = views.MessageView.as_view()(
            request,
            pk=user.profile.pk,
        )

        assert response.status_code == 200
        assert (
            "teammember_profile/team-member-send-message.html" in response.template_name
        )
        assert response.context_data["profile_instance"] == user.profile
        assert "form" in response.context_data

    def test_get_form_kwargs_overwrites_name_and_email(
        self,
        rf,
        user_factory,
    ):
        user = user_factory(is_superuser=False)
        request = make_request(
            rf,
            user,
            method="post",
            data={
                "name": "Untrusted name",
                "email": "untrusted@example.com",
                "subject": "Test subject",
                "body": "Test body",
            },
        )

        view = views.MessageView()
        view.request = request

        kwargs = view.get_form_kwargs()

        assert kwargs["data"]["name"] == user.profile.full_name
        assert kwargs["data"]["email"] == user.profile.email
        assert kwargs["data"]["subject"] == "Test subject"
        assert kwargs["data"]["body"] == "Test body"

    def test_get_form_kwargs_does_not_replace_data_on_get(
        self,
        rf,
        user_factory,
    ):
        user = user_factory(is_superuser=False)
        request = make_request(rf, user)

        view = views.MessageView()
        view.request = request

        kwargs = view.get_form_kwargs()

        assert "data" not in kwargs

    def test_get_success_url(self, monkeypatch):
        monkeypatch.setattr(
            views,
            "reverse_lazy",
            lambda name, kwargs: f"/{name}/{kwargs['pk']}/",
        )

        view = views.MessageView()
        view.kwargs = {"pk": 17}

        assert view.get_success_url() == "/teammember-send-message/17/"

    def test_form_valid_sets_profile_clears_parent_and_adds_message(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)

        message = SimpleNamespace(
            parent=object(),
            user_profile=None,
        )
        form = SimpleNamespace(instance=message)

        request = make_request(
            rf,
            user,
            method="post",
            path="/messages/",
        )

        view = views.MessageView()
        view.request = request
        view.service = SimpleNamespace(user_profile=user.profile)

        monkeypatch.setattr(
            views.CreateView,
            "form_valid",
            lambda self, form: HttpResponse("ok"),
        )

        response = view.form_valid(form)

        assert response.status_code == 200
        assert message.user_profile == user.profile
        assert message.parent is None
        assert get_message_texts(request) == ["Your message was sent"]

    def test_setup_raises_404_without_profile(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(user_profile=None)
        install_service(monkeypatch, "MessagePageService", service)

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.MessageView.as_view()(request, pk=1)


class TestProfileDashboardView:
    def test_get_context(self, rf, user_factory):
        user = user_factory(is_superuser=False)
        request = make_request(rf, user)

        response = views.ProfileDashboardView.as_view()(request)

        assert response.status_code == 200
        assert (
            "teammember_profile/user-profile-dashboard.html" in response.template_name
        )
        assert response.context_data["profile_instance"] == user.profile
        assert response.context_data["total_articles"] == 0
        assert response.context_data["total_views"] == 0
        assert response.context_data["total_comments"] == 0
        assert response.context_data["total_messages"] == 0
        assert response.context_data["total_pending_comments"] == 0
        assert response.context_data["total_unread_messages"] == 0

    def test_setup_raises_404_without_profile(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(user_profile=None)
        install_service(monkeypatch, "ProfileDashboardService", service)

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.ProfileDashboardView.as_view()(request)


class TestProfileArticlesListView:
    def test_get_articles_and_context(
        self,
        rf,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory(is_superuser=False)
        category = category_factory(
            user_profile=user.profile,
            name="profile-articles-view-category",
        )

        articles = [
            article_factory(
                user_profile=user.profile,
                category=category,
                title=f"Profile article {index}",
                status=Article.StatusChoices.PUBLISHED,
            )
            for index in range(4)
        ]

        request = make_request(rf, user)
        response = views.ProfileArticlesListView.as_view()(
            request,
            status="all",
        )

        assert response.status_code == 200
        assert "teammember_profile/user-profile-articles.html" in response.template_name
        assert response.context_data["profile_instance"] == user.profile
        assert response.context_data["status"] == "all"
        assert response.context_data["paginator"].count == 4
        assert response.context_data["is_paginated"] is True
        assert len(response.context_data["articles"]) == 3
        assert set(response.context_data["articles"]).issubset(set(articles))

    def test_passes_search_query_to_service(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=user.profile,
            status="all",
            get_articles=Mock(return_value=Article.objects.none()),
            get_context=Mock(return_value={}),
        )
        constructor = install_service(
            monkeypatch,
            "ProfileArticlesListService",
            service,
        )

        request = make_request(
            rf,
            user,
            path="/profile/articles/all/",
            data={"q": "search term"},
        )

        response = views.ProfileArticlesListView.as_view()(
            request,
            status="all",
        )

        assert response.status_code == 200
        constructor.assert_called_once_with(
            user=user,
            status="all",
            search_query="search term",
        )
        service.get_articles.assert_called_once()

    @pytest.mark.parametrize(
        ("result", "expected_message"),
        [
            (True, "Article was deleted"),
            (False, "Article wasn't deleted"),
        ],
    )
    def test_post_delete_article(
        self,
        rf,
        user_factory,
        monkeypatch,
        result,
        expected_message,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=user.profile,
            status="all",
            delete_article=Mock(return_value=result),
        )
        install_service(
            monkeypatch,
            "ProfileArticlesListService",
            service,
        )

        request = make_request(
            rf,
            user,
            method="post",
            path="/profile/articles/all/",
            data={
                "action": "delete",
                "article_id": "42",
            },
        )

        response = views.ProfileArticlesListView.as_view()(
            request,
            status="all",
        )

        assert response.status_code == 302
        assert response["Location"] == request.path
        service.delete_article.assert_called_once_with("42")
        assert get_message_texts(request) == [expected_message]

    def test_post_unknown_action(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=user.profile,
            status="all",
            delete_article=Mock(),
        )
        install_service(
            monkeypatch,
            "ProfileArticlesListService",
            service,
        )

        request = make_request(
            rf,
            user,
            method="post",
            path="/profile/articles/all/",
            data={"action": "unknown"},
        )

        response = views.ProfileArticlesListView.as_view()(
            request,
            status="all",
        )

        assert response.status_code == 302
        assert response["Location"] == request.path
        service.delete_article.assert_not_called()
        assert get_message_texts(request) == []

    def test_invalid_status_raises_404(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=user.profile,
            status=None,
        )
        install_service(
            monkeypatch,
            "ProfileArticlesListService",
            service,
        )

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.ProfileArticlesListView.as_view()(
                request,
                status="invalid",
            )

    def test_missing_profile_raises_404(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(user_profile=None, status="all")
        install_service(
            monkeypatch,
            "ProfileArticlesListService",
            service,
        )

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.ProfileArticlesListView.as_view()(
                request,
                status="all",
            )


class TestProfileCreateArticleView:
    def test_get_context(self, rf, user_factory):
        user = user_factory(is_superuser=False)
        request = make_request(rf, user)

        response = views.ProfileCreateArticleView.as_view()(request)

        assert response.status_code == 200
        assert (
            "teammember_profile/user-profile-create-article.html"
            in response.template_name
        )
        assert response.context_data["profile_instance"] == user.profile
        assert "form" in response.context_data

    def test_form_valid_assigns_profile_and_calls_service(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        article = Article(
            title="New draft",
            status=Article.StatusChoices.DRAFT,
        )
        form = SimpleNamespace(instance=article)
        set_article = Mock()

        view = views.ProfileCreateArticleView()
        view.request = make_request(rf, user, method="post")
        view.service = SimpleNamespace(
            user_profile=user.profile,
            set_article=set_article,
        )
        view.object = article

        monkeypatch.setattr(
            views.CreateView,
            "form_valid",
            lambda self, form: HttpResponse("ok"),
        )

        response = view.form_valid(form)

        assert response.status_code == 200
        assert article.user_profile == user.profile
        set_article.assert_called_once_with(article)

    def test_get_success_url_for_published_article(self):
        article = SimpleNamespace(
            status=Article.StatusChoices.PUBLISHED,
            get_absolute_url=lambda: "/articles/published/",
        )

        view = views.ProfileCreateArticleView()
        view.object = article

        assert view.get_success_url() == "/articles/published/"

    def test_get_success_url_for_draft_article(self, monkeypatch):
        monkeypatch.setattr(
            views,
            "reverse_lazy",
            lambda name, kwargs: f"/{name}/{kwargs['status']}/",
        )

        article = SimpleNamespace(status=Article.StatusChoices.DRAFT)
        view = views.ProfileCreateArticleView()
        view.object = article

        assert view.get_success_url() == "/profile-articles/all/"

    def test_setup_raises_404_without_profile(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(user_profile=None)
        install_service(monkeypatch, "ProfileArticleService", service)

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.ProfileCreateArticleView.as_view()(request)


class TestProfileUpdateArticleView:
    def test_get_article_and_context(
        self,
        rf,
        user_factory,
        category_factory,
        article_factory,
    ):
        user = user_factory(is_superuser=False)
        category = category_factory(
            user_profile=user.profile,
            name="update-article-view-category",
        )
        article = article_factory(
            user_profile=user.profile,
            category=category,
            title="Article to update",
        )

        request = make_request(rf, user)
        response = views.ProfileUpdateArticleView.as_view()(
            request,
            pk=article.pk,
        )

        assert response.status_code == 200
        assert (
            "teammember_profile/user-profile-create-article.html"
            in response.template_name
        )
        assert response.context_data["profile_instance"] == user.profile
        assert response.context_data["form"].instance == article

    def test_raises_404_when_article_does_not_exist(
        self,
        rf,
        user_factory,
    ):
        user = user_factory(is_superuser=False)
        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.ProfileUpdateArticleView.as_view()(
                request,
                pk=999999,
            )

    def test_raises_404_when_article_belongs_to_another_user(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        other_user = user_factory(is_superuser=False)

        foreign_article = SimpleNamespace(
            user_profile=other_user.profile,
        )
        service = SimpleNamespace(
            user_profile=user.profile,
            article=foreign_article,
        )
        install_service(
            monkeypatch,
            "ProfileArticleService",
            service,
        )

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.ProfileUpdateArticleView.as_view()(
                request,
                pk=123,
            )

    def test_get_success_url_for_published_article(self):
        article = SimpleNamespace(
            status=Article.StatusChoices.PUBLISHED,
            get_absolute_url=lambda: "/articles/published/",
        )
        view = views.ProfileUpdateArticleView()
        view.object = article

        assert view.get_success_url() == "/articles/published/"

    def test_get_success_url_for_draft_article(self, monkeypatch):
        monkeypatch.setattr(
            views,
            "reverse_lazy",
            lambda name, kwargs: f"/{name}/{kwargs['status']}/",
        )

        article = SimpleNamespace(status=Article.StatusChoices.DRAFT)
        view = views.ProfileUpdateArticleView()
        view.object = article

        assert view.get_success_url() == "/profile-articles/all/"

    def test_setup_raises_404_without_profile(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=None,
            article=None,
        )
        install_service(
            monkeypatch,
            "ProfileArticleService",
            service,
        )

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.ProfileUpdateArticleView.as_view()(
                request,
                pk=1,
            )

    def test_setup_raises_404_without_article(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=user.profile,
            article=None,
        )
        install_service(
            monkeypatch,
            "ProfileArticleService",
            service,
        )

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.ProfileUpdateArticleView.as_view()(
                request,
                pk=1,
            )


class TestProfileCommentsView:
    def test_get_comments_and_context(
        self,
        rf,
        user_factory,
        category_factory,
        article_factory,
        comment_factory,
    ):
        user = user_factory(is_superuser=False)
        category = category_factory(
            user_profile=user.profile,
            name="comments-view-category",
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

        request = make_request(rf, user)
        response = views.ProfileCommentsView.as_view()(
            request,
            status="all",
        )

        assert response.status_code == 200
        assert (
            "teammember_profile/user-profile-articles-comments.html"
            in response.template_name
        )
        assert response.context_data["profile_instance"] == user.profile
        assert response.context_data["status"] == "all"
        assert comment in response.context_data["comments"]

    def test_passes_search_query_to_service(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=user.profile,
            status="all",
            get_comments=Mock(return_value=Comment.objects.none()),
            get_context=Mock(return_value={}),
        )
        constructor = install_service(
            monkeypatch,
            "ProfileCommentsService",
            service,
        )

        request = make_request(
            rf,
            user,
            path="/profile/comments/all/",
            data={"q": "search term"},
        )

        response = views.ProfileCommentsView.as_view()(
            request,
            status="all",
        )

        assert response.status_code == 200
        constructor.assert_called_once_with(
            user=user,
            status="all",
            search_query="search term",
        )
        service.get_comments.assert_called_once()

    @pytest.mark.parametrize(
        ("action", "result", "expected_message", "method_name"),
        [
            ("approve", True, "Comment approved", "accept_comment"),
            ("approve", False, "Comment not approved", "accept_comment"),
            ("reject", True, "Comment rejected", "reject_comment"),
            ("reject", False, "Comment not rejected", "reject_comment"),
            ("delete", True, "Comment deleted", "delete_comment"),
            ("delete", False, "Comment not deleted", "delete_comment"),
            ("reply", True, "Reply was sent", "reply_comment"),
            ("reply", False, "Reply wasn't sent", "reply_comment"),
        ],
    )
    def test_post_actions(
        self,
        rf,
        user_factory,
        monkeypatch,
        action,
        result,
        expected_message,
        method_name,
    ):
        user = user_factory(is_superuser=False)

        methods = {
            "accept_comment": Mock(return_value=result),
            "reject_comment": Mock(return_value=result),
            "delete_comment": Mock(return_value=result),
            "reply_comment": Mock(return_value=result),
        }
        service = SimpleNamespace(
            user_profile=user.profile,
            status="all",
            **methods,
        )
        install_service(
            monkeypatch,
            "ProfileCommentsService",
            service,
        )

        request = make_request(
            rf,
            user,
            method="post",
            path="/profile/comments/all/",
            data={
                "action": action,
                "comment_id": "13",
                "parent_id": "21",
                "body": "Reply body",
            },
        )

        response = views.ProfileCommentsView.as_view()(
            request,
            status="all",
        )

        assert response.status_code == 302
        assert response["Location"] == request.path
        assert get_message_texts(request) == [expected_message]

        if action == "reply":
            service.reply_comment.assert_called_once_with(
                parent_id="21",
                body="Reply body",
            )
        else:
            getattr(service, method_name).assert_called_once_with("13")

    def test_post_unknown_action(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=user.profile,
            status="all",
            accept_comment=Mock(),
            reject_comment=Mock(),
            delete_comment=Mock(),
            reply_comment=Mock(),
        )
        install_service(
            monkeypatch,
            "ProfileCommentsService",
            service,
        )

        request = make_request(
            rf,
            user,
            method="post",
            path="/profile/comments/all/",
            data={"action": "unknown"},
        )

        response = views.ProfileCommentsView.as_view()(
            request,
            status="all",
        )

        assert response.status_code == 302
        assert response["Location"] == request.path
        assert get_message_texts(request) == []
        service.accept_comment.assert_not_called()
        service.reject_comment.assert_not_called()
        service.delete_comment.assert_not_called()
        service.reply_comment.assert_not_called()

    def test_invalid_status_raises_404(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=user.profile,
            status=None,
        )
        install_service(
            monkeypatch,
            "ProfileCommentsService",
            service,
        )

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.ProfileCommentsView.as_view()(
                request,
                status="invalid",
            )

    def test_missing_profile_raises_404(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=None,
            status="all",
        )
        install_service(
            monkeypatch,
            "ProfileCommentsService",
            service,
        )

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.ProfileCommentsView.as_view()(
                request,
                status="all",
            )


class TestProfileMessagesView:
    def test_get_messages_and_context(
        self,
        rf,
        user_factory,
        message_factory,
    ):
        user = user_factory(is_superuser=False)
        message = message_factory(
            user_profile=user.profile,
            is_read=False,
            is_deleted=False,
        )

        request = make_request(rf, user)
        response = views.ProfileMessagesView.as_view()(
            request,
            status="inbox",
        )

        assert response.status_code == 200
        assert (
            "teammember_profile/user-profile-articles-messages.html"
            in response.template_name
        )
        assert response.context_data["profile_instance"] == user.profile
        assert response.context_data["status"] == "inbox"
        assert message in response.context_data["messages_objects"]
        assert response.context_data["total_unread_messages"] == 1

    def test_passes_search_query_to_service(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=user.profile,
            status="all",
            get_messages=Mock(return_value=Message.objects.none()),
            get_context=Mock(return_value={}),
        )
        constructor = install_service(
            monkeypatch,
            "ProfileMessagesService",
            service,
        )

        request = make_request(
            rf,
            user,
            path="/profile/messages/all/",
            data={"q": "search term"},
        )

        response = views.ProfileMessagesView.as_view()(
            request,
            status="all",
        )

        assert response.status_code == 200
        constructor.assert_called_once_with(
            user=user,
            status="all",
            search_query="search term",
        )
        service.get_messages.assert_called_once()

    @pytest.mark.parametrize(
        ("action", "result", "expected_message", "method_name"),
        [
            (
                "readall",
                True,
                "Set all messages as read",
                "set_all_messages_as_read",
            ),
            (
                "readall",
                False,
                "Failed to set all messages as read",
                "set_all_messages_as_read",
            ),
            ("delete", True, "Message was deleted", "delete_message"),
            ("delete", False, "Failed to delete message", "delete_message"),
            ("archive", True, "Message was archived", "archive_message"),
            ("archive", False, "Failed to archive message", "archive_message"),
            ("reply", True, "Reply was sent", "reply_message"),
            ("reply", False, "Failed to reply message", "reply_message"),
        ],
    )
    def test_post_actions(
        self,
        rf,
        user_factory,
        monkeypatch,
        action,
        result,
        expected_message,
        method_name,
    ):
        user = user_factory(is_superuser=False)

        methods = {
            "set_all_messages_as_read": Mock(return_value=result),
            "delete_message": Mock(return_value=result),
            "archive_message": Mock(return_value=result),
            "reply_message": Mock(return_value=result),
        }
        service = SimpleNamespace(
            user_profile=user.profile,
            status="all",
            **methods,
        )
        install_service(
            monkeypatch,
            "ProfileMessagesService",
            service,
        )

        request = make_request(
            rf,
            user,
            method="post",
            path="/profile/messages/all/",
            data={
                "action": action,
                "message_id": "17",
                "reply_body": "Reply body",
            },
        )

        response = views.ProfileMessagesView.as_view()(
            request,
            status="all",
        )

        assert response.status_code == 302
        assert response["Location"] == request.path
        assert get_message_texts(request) == [expected_message]

        if action == "readall":
            service.set_all_messages_as_read.assert_called_once_with()
        elif action == "reply":
            service.reply_message.assert_called_once_with(
                "17",
                "Reply body",
            )
        else:
            getattr(service, method_name).assert_called_once_with("17")

    def test_post_reply_with_empty_body_does_not_call_service(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=user.profile,
            status="all",
            set_all_messages_as_read=Mock(),
            delete_message=Mock(),
            archive_message=Mock(),
            reply_message=Mock(),
        )
        install_service(
            monkeypatch,
            "ProfileMessagesService",
            service,
        )

        request = make_request(
            rf,
            user,
            method="post",
            path="/profile/messages/all/",
            data={
                "action": "reply",
                "message_id": "17",
                "reply_body": "",
            },
        )

        response = views.ProfileMessagesView.as_view()(
            request,
            status="all",
        )

        assert response.status_code == 302
        assert response["Location"] == request.path
        service.reply_message.assert_not_called()
        assert get_message_texts(request) == []

    def test_post_unknown_action(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=user.profile,
            status="all",
            set_all_messages_as_read=Mock(),
            delete_message=Mock(),
            archive_message=Mock(),
            reply_message=Mock(),
        )
        install_service(
            monkeypatch,
            "ProfileMessagesService",
            service,
        )

        request = make_request(
            rf,
            user,
            method="post",
            path="/profile/messages/all/",
            data={"action": "unknown"},
        )

        response = views.ProfileMessagesView.as_view()(
            request,
            status="all",
        )

        assert response.status_code == 302
        assert response["Location"] == request.path
        assert get_message_texts(request) == []
        service.set_all_messages_as_read.assert_not_called()
        service.delete_message.assert_not_called()
        service.archive_message.assert_not_called()
        service.reply_message.assert_not_called()

    def test_invalid_status_raises_404(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=user.profile,
            status=None,
        )
        install_service(
            monkeypatch,
            "ProfileMessagesService",
            service,
        )

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.ProfileMessagesView.as_view()(
                request,
                status="invalid",
            )

    def test_missing_profile_raises_404(
        self,
        rf,
        user_factory,
        monkeypatch,
    ):
        user = user_factory(is_superuser=False)
        service = SimpleNamespace(
            user_profile=None,
            status="all",
        )
        install_service(
            monkeypatch,
            "ProfileMessagesService",
            service,
        )

        request = make_request(rf, user)

        with pytest.raises(Http404):
            views.ProfileMessagesView.as_view()(
                request,
                status="all",
            )
