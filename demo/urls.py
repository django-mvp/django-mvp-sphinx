"""URL routes for the demo project."""

from django.urls import include, path
from mvp.mounted import mount
from mvp.views.account import SignInView

from demo.examples import views as examples
from demo.mounted import docs, staff_guide
from demo.views import OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    # Pages the guide shows as live examples. They are ordinary pages of the site.
    path("examples/contact/", examples.ContactView.as_view(), name="example_contact"),
    path("examples/status/", examples.StatusView.as_view(), name="example_status"),
    path("examples/slow/", examples.SlowView.as_view(), name="example_slow"),
    path("examples/staff/", examples.StaffNoteView.as_view(), name="example_staff"),
    path("examples/broken/", examples.BrokenView.as_view(), name="example_broken"),
    mount("docs/", docs),
    mount("staff-guide/", staff_guide),
    # The shell's sign-in page, ahead of the include, which has none of its own.
    path("accounts/login/", SignInView.as_view(), name="account_login"),
    # The application shell's sign-out and account routes.
    path("accounts/", include("django.contrib.auth.urls")),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
