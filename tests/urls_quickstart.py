"""The urlconf of a project that followed the quickstart: step 4's app and mount."""

from django.conf import settings
from mvp.mounted import mount

from mvp_sphinx.mounted import DocumentationApp
from tests.urls import urlpatterns as suite_urlpatterns

docs = DocumentationApp(
    build_dir=settings.BASE_DIR / "docs" / "_build" / "json",
    namespace="quickstart",
)

urlpatterns = [*suite_urlpatterns, mount("help/guide/", docs)]
