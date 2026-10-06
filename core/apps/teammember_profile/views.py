from django.http import Http404
from django.views.generic import ListView

from apps.blog.models import Article
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
