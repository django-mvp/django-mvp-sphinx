"""The demo project's documentation apps: the open guide and the staff-only guide."""

from django.utils.translation import gettext_lazy as _
from flex_menu.checks import user_is_staff

from demo.settings import BASE_DIR
from mvp_sphinx.mounted import DocumentationApp

docs = DocumentationApp(build_dir=BASE_DIR / "demo" / "docs" / "_build" / "json")
staff_guide = DocumentationApp(
    build_dir=BASE_DIR / "demo" / "staff_guide" / "_build" / "json",
    name=_("Staff guide"),
    namespace="staff_guide",
    check=user_is_staff,
)
