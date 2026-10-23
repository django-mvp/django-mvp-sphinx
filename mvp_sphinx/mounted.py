"""The documentation app a host project mounts to serve its docs build."""

import logging
from typing import Any

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.templatetags.static import static
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from mvp.mounted import MountedApp

from mvp_sphinx.docs_build import DocsBuild
from mvp_sphinx.examples import LiveExamples
from mvp_sphinx.extracts import LinkRewriter, PageExtract, SectionFinder, plain_text
from mvp_sphinx.menus import DocumentationMenu
from mvp_sphinx.page_body import BodyRewriter
from mvp_sphinx.views import PageView, SearchView

logger = logging.getLogger(__name__)


class DocumentationApp(MountedApp):
    """One docs build, served under the prefix a host project mounts it at.

    The host creates an instance and mounts it, then adds the entry that
    ``menu_item()`` returns to its own menus. A second build is a second
    instance with its own ``namespace``.

    ``namespace`` is the knob for the app's URLs, landing and menu: they are
    derived from it when the instance is created, so ``urls``, ``landing`` or
    ``menu`` passed by keyword are overwritten.

    Args:
        build_dir: The directory ``sphinx-build -b json`` wrote to. It is not
            read until a page is requested, so it may not exist yet.
        source_dir: The Sphinx source directory the build is made from, the one
            that holds ``conf.py``. Only the ``build_docs`` management command
            reads it, to build from it into ``build_dir``. Serving never does,
            so leave it out when the build is made some other way.
        name: What the documentation is called, in the page title, breadcrumbs
            and the host's menu entry.
        icon: The icon name for the host's menu entry.
        namespace: The URL namespace, ``docs`` unless a host mounts several.
        view_class: The view that renders a page.
        check: Who may read the documentation: ``True`` for everyone (the
            default), ``False`` for no one, or a function of the request, such
            as ``user_is_authenticated`` from ``flex_menu.checks`` for signed-in
            people only. The rule covers every address under the app, images and
            downloads included, and its menu entry. It is asked on every request.
            An anonymous reader it excludes is sent to sign in and back, and a
            signed-in one gets the project's 403 page. An error it raises is a
            server error.

    Raises:
        ImproperlyConfigured: ``build_dir`` was not given.

    Example::

        docs = DocumentationApp(build_dir=BASE_DIR / "docs" / "_build" / "json")

        urlpatterns = [mount("docs/", docs)]
    """

    name = _("Documentation")
    icon = "document"
    namespace = "docs"
    build_dir: Any = None
    source_dir: Any = None
    view_class = PageView
    urls: Any = []

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self.build_dir is None:
            raise ImproperlyConfigured(
                "DocumentationApp needs a build_dir, the directory sphinx-build -b json wrote to."
            )
        view = self.view_class.as_view(app=self)
        self.urls = (
            [
                path("", view, name="front_page"),
                path("search/", SearchView.as_view(app=self), name="search"),
                path("<path:path>", view, name="page"),
            ],
            self.namespace,
        )
        self.landing = f"{self.namespace}:front_page"
        # The shell processes every app's menu on host pages no mount serves.
        self.menu = DocumentationMenu(f"mvp_sphinx-{self.namespace}", app=self)

    def page_extract(self, address: str, request: HttpRequest) -> PageExtract | None:
        """Return a page of the docs build, for use outside the documentation app.

        Args:
            address: The page's address below the app's prefix, such as
                ``"reference/accounts/"``. The empty address is the front page.
            request: The request being served.

        Returns:
            The page's extract, or ``None`` when the reader may not read the
            app, or the build or the page is missing or broken. A page that is
            missing or can't be read is logged as a warning.
        """
        if not self.has_permission(request):
            return None
        page_path, *fragment = address.split("#", 1)
        anchor = fragment[0] if fragment else ""
        try:
            page = DocsBuild(self.build_dir).page(page_path)
        except (OSError, ValueError):
            logger.warning("%s: the page at %r can't be read.", self.namespace, address)
            return None
        if page is None:
            logger.warning("%s: no page at %r.", self.namespace, address)
            return None
        body = page.get("body", "")
        found = SectionFinder(body, anchor)
        if found.start is None or found.end is None:
            logger.warning("%s: no section at %r.", self.namespace, address)
            return None
        if page_path:
            page_url = reverse(f"{self.namespace}:page", kwargs={"path": page_path})
        else:
            page_url = reverse(f"{self.namespace}:front_page")
        linked = LinkRewriter.rewrite(body[found.start : found.end], page_url)
        rewritten = BodyRewriter.parse(linked).splice()
        # Live examples need the documentation app's own page around them.
        kept = "".join(
            str(part["html"])
            for part in LiveExamples.parts(rewritten)
            if "html" in part
        )
        content = format_html(
            '<link rel="stylesheet" href="{}">'
            '<div class="prose mvp-sphinx-content">{}</div>',
            static("mvp_sphinx/content.css"),
            mark_safe(kept),  # noqa: S308 the host's own docs build
        )
        if anchor:
            return PageExtract(
                content=content, title=found.title, url=f"{page_url}#{anchor}"
            )
        return PageExtract(
            content=content, title=plain_text(page.get("title", "")), url=page_url
        )
