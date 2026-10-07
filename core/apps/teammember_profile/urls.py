from django.urls import path

from apps.teammember_profile.views import (
    TeamMemberPublicView,
    MessageView,
    ProfileDashboardView,
    ProfileArticlesListView,
    ProfileCreateArticleView,
)

urlpatterns = [
    path("team-member/<int:pk>/", TeamMemberPublicView.as_view(), name="teammember"),
    path(
        "team-member/<int:pk>/send-message/",
        MessageView.as_view(),
        name="teammember-send-message",
    ),
    path(
        "profile/<int:pk>/dashboard/",
        ProfileDashboardView.as_view(),
        name="profile-dashboard",
    ),
    path(
        "profile/<int:pk>/articles/<str:status>/",
        ProfileArticlesListView.as_view(),
        name="profile-articles",
    ),
    path(
        "profile/<int:pk>/create-article/",
        ProfileCreateArticleView.as_view(),
        name="profile-create-article",
    ),
]
