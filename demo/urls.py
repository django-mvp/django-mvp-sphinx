"""URL routes for the demo project."""

from django.urls import include, path
from mvp.mounted import mount
from mvp.views.account import SignInView

from demo.mounted import docs, staff_guide
from demo.views import OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    mount("docs/", docs),
    mount("staff-guide/", staff_guide),
    # The shell's sign-in page, ahead of the include, which has none of its own.
    path("accounts/login/", SignInView.as_view(), name="account_login"),
    # The application shell's sign-out and account routes.
    path("accounts/", include("django.contrib.auth.urls")),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
