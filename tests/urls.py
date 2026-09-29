"""The suite's urlconf: the demo project's routes plus any test-only route."""

from django.utils.translation import gettext_lazy as _
from mvp.mounted import mount

from demo.settings import BASE_DIR
from demo.urls import urlpatterns as demo_urlpatterns
from mvp_sphinx.mounted import DocumentationApp

# A second documentation app beside the demo's, at a prefix of two segments.
# Tests point it at a build through the handbook_app fixture.
handbook = DocumentationApp(
    build_dir=BASE_DIR / "tests" / "handbook-not-built",
    name=_("Administrator's handbook"),
    namespace="handbook",
)

urlpatterns = [*demo_urlpatterns, mount("manuals/admin/", handbook)]
