from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView

from apps.blog.forms import MessageForm
from apps.blog.models import Article, Message
from apps.teammember_profile.services.message_page_service import MessagePageService
from apps.teammember_profile.services.profile_articles_list_view_service import (
    ProfileArticlesListService,
)
from apps.teammember_profile.services.profile_dashboard_service import (
    ProfileDashboardService,
)
from apps.teammember_profile.services.public_teammember_service import (
    PublicTeamMemberService,
)


# Create your views here.
class TeamMemberPublicView(ListView):
    model = Article
    paginate_by = 4
    template_name = "teammember_profile/team-member.html"
    context_object_name = "articles"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.service = PublicTeamMemberService(
            profile_id=self.kwargs["pk"],
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
        return reverse_lazy("teammember-send-message", kwargs={"pk": self.kwargs["pk"]})

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.service = MessagePageService(
            profile_id=self.kwargs["pk"],
        )
        if self.service.user_profile is None:
            raise Http404

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
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
        instance = form.save(commit=False)

        instance.parent = None
        instance.user_profile = self.service.user_profile

        instance.save()

        messages.success(self.request, "Your message was sent")

        return super().form_valid(form)


class ProfileDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "teammember_profile/user-profile-dashboard.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.service = ProfileDashboardService(self.kwargs["pk"])
        if self.service.user_profile is None:
            raise Http404

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(self.service.get_context(view_context=context))
        return context


class ProfileArticlesListView(ListView):
    model = Article
    paginate_by = 6
    template_name = "teammember_profile/user-profile-articles.html"
    context_object_name = "articles"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.service = ProfileArticlesListService(
            profile_id=self.kwargs["pk"],
            status=self.kwargs["status"],
            search_query=self.request.GET.get("q"),
        )
        if self.service.user_profile is None:
            raise Http404

        if self.service.status is None:
            raise Http404

    def get_queryset(self):
        return self.service.get_articles()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(self.service.get_context(view_context=context))
        return context
