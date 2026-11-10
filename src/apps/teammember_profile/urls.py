from django.urls import path

from apps.teammember_profile.views import (
    TeamMemberPublicView,
    MessageView,
    ProfileDashboardView,
    ProfileArticlesListView,
    ProfileCreateArticleView,
    ProfileUpdateArticleView,
    ProfileCommentsView,
    ProfileMessagesView,
    ProfileEditView,
)


urlpatterns = [
    path(
        "team-member/<int:pk>/",
        TeamMemberPublicView.as_view(),
        name="teammember",
    ),
    path(
        "team-member/<int:pk>/send-message/",
        MessageView.as_view(),
        name="teammember-send-message",
    ),
    path(
        "profile/dashboard/",
        ProfileDashboardView.as_view(),
        name="profile-dashboard",
    ),
    path(
        "profile/articles/<str:status>/",
        ProfileArticlesListView.as_view(),
        name="profile-articles",
    ),
    path(
        "profile/create-article/",
        ProfileCreateArticleView.as_view(),
        name="profile-create-article",
    ),
    path(
        "profile/edit-article/<int:pk>/",
        ProfileUpdateArticleView.as_view(),
        name="profile-update-article",
    ),
    path(
        "profile/comments/<str:status>/",
        ProfileCommentsView.as_view(),
        name="profile-comments",
    ),
    path(
        "profile/messages/<str:status>/",
        ProfileMessagesView.as_view(),
        name="profile-messages",
    ),
    path(
        "profile/<int:pk>/edit/",
        ProfileEditView.as_view(),
        name="profile-edit",
    ),
]
