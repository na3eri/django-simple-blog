from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    TemplateView,
    UpdateView,
)

from apps.blog.forms import MessageForm, ArticleForm
from apps.blog.models import Article, Message
from apps.teammember_profile.services.message_page_service import (
    MessagePageService,
)
from apps.teammember_profile.services.profile_article_service import (
    ProfileArticleService,
)
from apps.teammember_profile.services.profile_articles_list_view_service import (
    ProfileArticlesListService,
)
from apps.teammember_profile.services.profile_comments_service import (
    ProfileCommentsService,
)
from apps.teammember_profile.services.profile_dashboard_service import (
    ProfileDashboardService,
)
from apps.teammember_profile.services.profile_messages_service import (
    ProfileMessagesService,
)
from apps.teammember_profile.services.public_teammember_service import (
    PublicTeamMemberService,
)
from apps.blog.models import Comment


class TeamMemberPublicView(ListView):
    model = Article
    paginate_by = 4
    template_name = "teammember_profile/team-member.html"
    context_object_name = "articles"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.service = PublicTeamMemberService(
            user=request.user,
        )

        if self.service.user_profile is None:
            raise Http404

    def get_queryset(self):
        return self.service.get_articles()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(self.service.get_context(view_context=context))

        return context


class MessageView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "teammember_profile/team-member-send-message.html"

    def get_success_url(self):
        return reverse_lazy(
            "teammember-send-message",
            kwargs={
                "pk": self.kwargs["pk"],
            },
        )

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.service = MessagePageService(
            user=request.user,
        )

        if self.service.user_profile is None:
            raise Http404

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context.update(self.service.get_context(view_context=context))

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.method == "POST":
            data = kwargs["data"].copy()

            data["name"] = self.request.user.profile.full_name
            data["email"] = self.request.user.profile.email

            kwargs["data"] = data

        return kwargs

    def form_valid(self, form):
        form.instance.parent = None
        form.instance.user_profile = self.service.user_profile

        messages.success(
            self.request,
            "Your message was sent",
        )

        return super().form_valid(form)


class ProfileDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "teammember_profile/user-profile-dashboard.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.service = ProfileDashboardService(
            user=request.user,
        )

        if self.service.user_profile is None:
            raise Http404

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context.update(self.service.get_context(view_context=context))

        return context


class ProfileArticlesListView(LoginRequiredMixin, ListView):
    model = Article
    paginate_by = 3
    template_name = "teammember_profile/user-profile-articles.html"
    context_object_name = "articles"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.service = ProfileArticlesListService(
            user=request.user,
            status=self.kwargs["status"],
            search_query=request.GET.get("q"),
        )

        if self.service.user_profile is None:
            raise Http404

        if self.service.status is None:
            raise Http404

    def get_queryset(self):
        return self.service.get_articles()

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context.update(self.service.get_context(view_context=context))

        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")

        if action == "delete":
            article_id = request.POST.get("article_id")
            result = self.service.delete_article(article_id)
            if result:
                messages.success(request, "Article was deleted")
            else:
                messages.error(request, "Article wasn't deleted")

        return redirect(request.path)


class ProfileCreateArticleView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "teammember_profile/user-profile-create-article.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.service = ProfileArticleService(
            user_id=request.user.id,
        )

        if self.service.user_profile is None:
            raise Http404

    def get_success_url(self):
        if self.object.status != Article.StatusChoices.DRAFT:
            return self.object.get_absolute_url()

        return reverse_lazy(
            "profile-articles",
            kwargs={
                "status": "all",
            },
        )

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context.update(self.service.get_context(view_context=context))

        return context

    def form_valid(self, form):
        form.instance.user_profile = self.service.user_profile

        response = super().form_valid(form)

        self.service.set_article(self.object)

        return response


class ProfileUpdateArticleView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "teammember_profile/user-profile-create-article.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.service = ProfileArticleService(
            user_id=request.user.id,
            article_id=self.kwargs["pk"],
        )

        if self.service.user_profile is None:
            raise Http404

        if self.service.article is None:
            raise Http404

        # بررسی مالکیت مقاله
        if self.service.article.user_profile.user_id != request.user.id:
            raise Http404

    def get_queryset(self):
        return self.service.get_article_queryset(self.kwargs["pk"])

    def get_success_url(self) -> str:
        if self.object.status == Article.StatusChoices.DRAFT:
            return reverse_lazy(
                "profile-articles",
                kwargs={
                    "status": "all",
                },
            )

        return self.object.get_absolute_url()

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context.update(self.service.get_context(view_context=context))

        return context


class ProfileCommentsView(LoginRequiredMixin, ListView):
    model = Comment
    paginate_by = 3
    template_name = "teammember_profile/user-profile-articles-comments.html"
    context_object_name = "comments"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.service = ProfileCommentsService(
            user=request.user,
            status=self.kwargs["status"],
            search_query=request.GET.get("q"),
        )

        if self.service.user_profile is None:
            raise Http404

        if self.service.status is None:
            raise Http404

    def get_queryset(self):
        return self.service.get_comments()

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context.update(self.service.get_context(view_context=context))

        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        comment_id = request.POST.get("comment_id")

        if action == "approve":
            result = self.service.accept_comment(comment_id)
            if result:
                messages.success(request, "Comment approved")
            else:
                messages.error(request, "Comment not approved")

        if action == "reject":
            result = self.service.reject_comment(comment_id)
            if result:
                messages.success(request, "Comment rejected")
            else:
                messages.error(request, "Comment not rejected")

        if action == "delete":
            result = self.service.delete_comment(comment_id)
            if result:
                messages.success(request, "Comment deleted")
            else:
                messages.error(request, "Comment not deleted")

        if action == "reply":
            parent_id = self.request.POST.get("parent_id")
            body = self.request.POST.get("body")
            result = self.service.reply_comment(parent_id=parent_id, body=body)
            if result:
                messages.success(request, "Reply was sent")
            else:
                messages.error(request, "Reply wasn't sent")

        return redirect(request.path)


class ProfileMessagesView(LoginRequiredMixin, ListView):
    model = Message
    paginate_by = 5
    template_name = "teammember_profile/user-profile-articles-messages.html"
    context_object_name = "messages_objects"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.service = ProfileMessagesService(
            user=request.user,
            status=self.kwargs["status"],
            search_query=request.GET.get("q"),
        )

        if self.service.user_profile is None:
            raise Http404

        if self.service.status is None:
            raise Http404

    def get_queryset(self):
        return self.service.get_messages()

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context.update(self.service.get_context(view_context=context))

        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")

        if action == "readall":
            result = self.service.set_all_messages_as_read()
            if result:
                messages.success(request, "Set all messages as read")
            else:
                messages.error(request, "Failed to set all messages as read")

        if action == "delete":
            message_id = request.POST.get("message_id")
            result = self.service.delete_message(message_id)
            if result:
                messages.success(request, "Message was deleted")
            else:
                messages.error(request, "Failed to delete message")

        if action == "archive":
            message_id = request.POST.get("message_id")
            result = self.service.archive_message(message_id)
            if result:
                messages.success(request, "Message was archived")
            else:
                messages.error(request, "Failed to archive message")

        if action == "reply":
            message_id = request.POST.get("message_id")
            reply_body = self.request.POST.get("reply_body")
            if reply_body:
                result = self.service.reply_message(message_id, reply_body)

                if result:
                    messages.success(request, "Reply was sent")
                else:
                    messages.error(request, "Failed to reply message")

        return redirect(request.path)
