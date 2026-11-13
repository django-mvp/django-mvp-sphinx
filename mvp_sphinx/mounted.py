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
from mvp.config import MVP_CONFIG
from mvp.mounted import MountedApp
from mvp.search import Result, register, registered
from mvp.search.registry import default_registry

from mvp_sphinx.docs_build import DocsBuild
from mvp_sphinx.examples import LiveExamples
from mvp_sphinx.extracts import LinkRewriter, PageExtract, SectionFinder, plain_text
from mvp_sphinx.menus import DocumentationMenu
from mvp_sphinx.page_body import BodyRewriter
from mvp_sphinx.search import DocsSearch
from mvp_sphinx.views import BranchView, PageView, SearchView

logger = logging.getLogger(__name__)


class DocumentationApp(MountedApp):
    """One docs build, served under the prefix a host project mounts it at.

    The host creates an instance and mounts it, then adds the entry that
    ``menu_item()`` returns to its own menus. A second build is a second
    instance with its own ``namespace``.

    ``namespace`` is the knob for the app's URLs, landing and menu: they are
    derived from it when the instance is created, so ``urls``, ``landing`` or
    ``menu`` passed by keyword are overwritten.

    Creating the instance also registers the app's pages as a kind of result in
    django-mvp's site search, named ``mvp_sphinx-<namespace>`` and held in
    ``search_kind``. The first instance under a namespace registers it, and the
    kind searches whichever app is mounted under that namespace in the URLconf
    the request is served from.

    Args:
        build_dir: The directory ``sphinx-build -b json`` wrote to. It is not
            read until a page is requested, so it may not exist yet. It may
            also be a function of the request that returns the directory, for
            a project that serves a build of its own to each site: every
            request is then served wholly from the build chosen for it, its
            pages, files, search, extracts and sidebar alike.
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
                path("contents/", BranchView.as_view(app=self), name="branch"),
                path("<path:path>", view, name="page"),
            ],
            self.namespace,
        )
        self.landing = f"{self.namespace}:front_page"
        # The shell processes every app's menu on host pages no mount serves.
        self.menu = DocumentationMenu(f"mvp_sphinx-{self.namespace}", app=self)
        self.search_kind = f"mvp_sphinx-{self.namespace}"
        if self.search_kind not in {kind.name for kind in registered()}:
            register(
                DocumentationPages(self.namespace),
                name=self.search_kind,
                label=self.name,
                icon=self.icon,
            )

    def in_site_search(self) -> bool:
        """Say whether django-mvp's site search stands in for the app's own.

        Returns:
            ``True`` when the navbar holds the site's search and the search
            uses this app's kind, so the site's search finds the app's pages.
        """
        return "mvp.actions.search" in MVP_CONFIG["layout"]["navbar"]["end"] and any(
            kind.name == self.search_kind for kind in default_registry.active()
        )

    def address(self, path: str, anchor: str = "") -> str:
        """Return the address of a page of the app, at a section or not.

        Args:
            path: The page's address below the app's prefix, ``""`` for the
                front page.
            anchor: The section's anchor, or ``""`` for the top of the page.

        Returns:
            The page's address under the app, and ``#`` with the anchor when
            there is one.
        """
        if path:
            address = reverse(f"{self.namespace}:page", kwargs={"path": path})
        else:
            address = reverse(f"{self.namespace}:front_page")
        return f"{address}#{anchor}" if anchor else address

    def build_dir_for(self, request: HttpRequest) -> Any:
        """Return the build directory that serves ``request``.

        Args:
            request: The request being served.

        Returns:
            ``build_dir``, or what it returns for ``request`` when it is a
            function.
        """
        if callable(self.build_dir):
            return self.build_dir(request)
        return self.build_dir

    def page_extract(self, address: str, request: HttpRequest) -> PageExtract | None:
        """Return a page of the docs build, for use outside the documentation app.

        Args:
            address: The page's address below the app's prefix, such as
                ``"reference/accounts"``, with a section's anchor after ``#`` or
                not. The trailing slash may be left out. The empty address is
                the front page.
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
        if page_path and not page_path.endswith("/"):
            # The address a reader without the slash is redirected to.
            page_path += "/"
        try:
            page = DocsBuild(self.build_dir_for(request)).page(page_path)
        except (OSError, ValueError):
            logger.warning("%s: the page at %r can't be read.", self.namespace, address)
            return None
        if page is None:
            logger.warning("%s: no page at %r.", self.namespace, address)
            return None
        body = page.get("body", "")
        found = SectionFinder(body, anchor)
        if found.heading_start is None or found.start is None:
            logger.warning("%s: no section at %r.", self.namespace, address)
            return None
        if anchor:
            if found.end is None:
                logger.warning("%s: no section at %r.", self.namespace, address)
                return None
            markup = body[found.start : found.end]
        else:
            # A whole page is its body less the title, whatever follows the title.
            markup = body[: found.heading_start] + body[found.start :]
        page_url = self.address(page_path)
        linked = LinkRewriter.rewrite(markup, page_url)
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


class DocumentationPages:
    """Find the pages of one documentation app, for django-mvp's site search.

    The app is looked up by its namespace among the mounts of the URLconf the
    request is served from, so the search follows the app that serves the
    request's pages, and finds nothing where no app is mounted under it.

    Args:
        namespace: The namespace of the documentation app to search.
    """

    def __init__(self, namespace: str) -> None:
        self.namespace = namespace

    def __call__(self, query: str, request: HttpRequest) -> list[Result]:
        """Return the app's pages holding every word of ``query``, best first.

        Args:
            query: What the reader typed.
            request: The request the search is for.

        Returns:
            One result per page, in the order the app's own search lists them.
            Each result's where line is the titles above the page in the
            contents, two at most and the outermost first, or the app's name
            when nothing is above it. Empty when the app is not mounted, the
            reader may not read it, or its build has no usable search data.
        """
        app = next(
            (
                mount.app
                for mount in MountedApp.mounts(request)
                if isinstance(mount.app, DocumentationApp)
                and mount.app.namespace == self.namespace
            ),
            None,
        )
        if app is None or not app.has_permission(request):
            return []
        build = DocsBuild(app.build_dir_for(request))
        found = DocsSearch(build).results(query) or []
        trails = build.trails() if found else {}
        return [
            Result(
                title=hit["title"],
                url=app.address(hit["path"], hit["anchor"]),
                where=" · ".join(trails.get(hit["path"], [])[:2]) or str(app.name),
                passage=hit["passage"],
            )
            for hit in found
        ]
