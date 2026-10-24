"""URL routes for the demo project."""

from django.urls import include, path
from mvp.mounted import mount
from mvp.views.account import SignInView

from demo import views
from demo.examples import views as examples
from demo.mounted import docs, staff_guide

urlpatterns = [
    path("", views.OverviewView.as_view(), name="overview"),
    # Screens whose info dialog holds a page, or a section, of a guide.
    path("info/whole-page/", views.WholePageView.as_view(), name="info_whole_page"),
    path("info/section/", views.SectionView.as_view(), name="info_section"),
    path("info/notices/", views.NoticesView.as_view(), name="info_notices"),
    path("info/staff/", views.StaffOnlyView.as_view(), name="info_staff"),
    path("info/moved/", views.MissingPageView.as_view(), name="info_moved"),
    # A screen whose template places a section of the guide with the template tag.
    path("in-page/", views.InPageView.as_view(), name="in_page"),
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
