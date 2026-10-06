from django.urls import path

from apps.teammember_profile.views import TeamMemberPublicView

urlpatterns = [
    path("team-member/<int:pk>/", TeamMemberPublicView.as_view(), name="teammember"),
]
