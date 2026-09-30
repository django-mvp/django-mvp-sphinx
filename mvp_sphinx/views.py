"""The view that renders a page of the docs build."""

import mimetypes
from html import unescape
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
)
from django.http.response import HttpResponseBase
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from mvp.views.base import PageMixin

from mvp_sphinx.docs_build import DocsBuild
from mvp_sphinx.page_body import BodyRewriter
from mvp_sphinx.search import DocsSearch

if TYPE_CHECKING:
    from mvp_sphinx.mounted import DocumentationApp


class PageView(PageMixin, TemplateView):
    """Render the page a request names, inside the application shell.

    The documentation app binds itself through ``as_view(app=...)``, and the
    view reads the app's ``build_dir`` on every request, so a rebuilt docs build
    is served without a restart.

    Attributes:
        app: The documentation app this view answers for.
    """

    template_name = "mvp_sphinx/page.html"
    app: "DocumentationApp" = None  # type: ignore[assignment]

    # A file answers with a streaming response, which is not an HttpResponse.
    def get(  # type: ignore[override]
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        """Serve the file or page at the address, or redirect to its slashed form.

        An address without its trailing slash redirects permanently, query
        string kept, when the slashed address has a page; otherwise it is not
        found and the host's own 404 answers.

        Args:
            request: The request being served.
            *args: Positional URL arguments, unused.
            **kwargs: URL arguments; ``path`` is the address below the app's prefix.

        Returns:
            The file, the rendered page, or a permanent redirect.

        Raises:
            Http404: The docs build has no file or page at that address.
            json.JSONDecodeError: A page's file is not valid JSON, a server error.
        """
        build = DocsBuild(self.app.build_dir)
        path = kwargs.get("path", "")
        target = build.file(path)
        if target is not None:
            content_type = mimetypes.guess_type(target.name)[0]
            return FileResponse(
                target.open("rb"),
                content_type=content_type or "application/octet-stream",
            )
        page = build.page(path)
        if page is None:
            if path and not path.endswith("/") and build.page(f"{path}/") is not None:
                return HttpResponsePermanentRedirect(
                    request.get_full_path(force_append_slash=True)
                )
            raise Http404
        self.page_data = page
        # The body is the host's own docs build, trusted as it always was.
        body = mark_safe(BodyRewriter.rewrite(page.get("body", "")))  # noqa: S308
        return self.render_to_response(self.get_context_data(page_data=page, body=body))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add the address of the app's search, which every page offers."""
        context = super().get_context_data(**kwargs)
        context["search_url"] = reverse(f"{self.app.namespace}:search")
        return context

    @staticmethod
    def plain_text(markup: str) -> str:
        """Return the text of a title Sphinx wrote as HTML.

        Args:
            markup: A title as it appears in a page's JSON, possibly with inline
                markup such as ``<code>``.

        Returns:
            The title's text, unescaped, ready for a template to escape.
        """
        return unescape(strip_tags(markup))

    def get_page_title(self) -> str:
        """Return the page's title as plain text, for the tab."""
        # Sphinx's general index and search pages carry no title.
        return self.plain_text(self.page_data.get("title", ""))

    def get_breadcrumbs(self) -> list[dict[str, Any]]:
        """Return the trail from the app's front page down to this page.

        The front page's trail is the app's name alone. On any other page the
        app's name links to the front page, each parent links to its own page,
        and the page itself has no link.

        Returns:
            The breadcrumbs, each a dict with ``text`` and, except the last,
            ``href``.
        """
        if self.kwargs.get("path", "") == "":
            return [{"text": self.app.name}]
        crumbs: list[dict[str, Any]] = [
            {"text": self.app.name, "href": reverse(f"{self.app.namespace}:front_page")}
        ]
        for parent in self.page_data.get("parents", []):
            crumbs.append(
                {
                    "text": self.plain_text(parent["title"]),
                    "href": urljoin(self.request.path, parent["link"]),
                }
            )
        crumbs.append({"text": self.get_page_title()})
        return crumbs


class SearchView(PageMixin, TemplateView):
    """Render the results of a search of the documentation app's own pages.

    The documentation app binds itself through ``as_view(app=...)``, and every
    search reads the docs build as it is on disk, so a rebuilt docs build is
    searchable without a restart.

    Attributes:
        app: The documentation app this view answers for.
    """

    template_name = "mvp_sphinx/search.html"
    app: "DocumentationApp" = None  # type: ignore[assignment]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Render the pages holding the words of the ``q`` query parameter.

        Args:
            request: The request being served.
            *args: Positional URL arguments, unused.
            **kwargs: URL arguments, unused.

        Returns:
            The results page. Its ``results`` are ``None`` when the build has no
            usable search data, so the page can say search is unavailable.

        Raises:
            Http404: The docs build does not exist, as for every page address.
        """
        build = DocsBuild(self.app.build_dir)
        if not build.root.is_dir():
            raise Http404
        self.query = request.GET.get("q", "")
        found = DocsSearch(build).results(self.query)
        results = None
        if found is not None:
            results = [{**result, "href": self.href(result)} for result in found]
        return self.render_to_response(
            self.get_context_data(query=self.query, results=results)
        )

    def href(self, result: dict[str, str]) -> str:
        """Return the address of a result's page, at its section when it has one.

        Args:
            result: A result from ``DocsSearch.results``.

        Returns:
            The page's address under the documentation app, and ``#`` with the
            section's anchor when the result names one.
        """
        namespace = self.app.namespace
        if result["path"]:
            address = reverse(f"{namespace}:page", kwargs={"path": result["path"]})
        else:
            address = reverse(f"{namespace}:front_page")
        return f"{address}#{result['anchor']}" if result["anchor"] else address

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add the address of the app's search, which the form submits to."""
        context = super().get_context_data(**kwargs)
        context["search_url"] = reverse(f"{self.app.namespace}:search")
        return context

    def get_page_title(self) -> str:
        """Return the title of the results page, naming the words searched for."""
        if self.query.strip():
            return _("Search: %(query)s") % {"query": self.query}
        return _("Search")

    def get_breadcrumbs(self) -> list[dict[str, Any]]:
        """Return the trail from the app's front page to the results page.

        Returns:
            The breadcrumbs: the app's name linking to its front page, then the
            results page itself.
        """
        return [
            {
                "text": self.app.name,
                "href": reverse(f"{self.app.namespace}:front_page"),
            },
            {"text": _("Search")},
        ]
