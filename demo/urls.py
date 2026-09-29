"""URL routes for the demo project."""

from django.urls import include, path

from demo.views import OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    # The application shell's sign-in, sign-out and account routes.
    path("accounts/", include("django.contrib.auth.urls")),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
