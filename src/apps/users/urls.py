from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

urlpatterns = [
    path("signin/", views.login_view, name="signin"),
    path("signout/", views.signout_view, name="signout"),
    path(
        "reset_password/",
        auth_views.PasswordResetView.as_view(
            template_name="users/reset_password.html",
            form_class=CustomPasswordResetForm,
        ),
        name="reset_password",
    ),
    path(
        "password_reset_done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/reset_password_sent.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/reset_password_reset.html",
            form_class=CustomSetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
