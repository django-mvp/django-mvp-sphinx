"""The view that renders a page of the docs build."""

import mimetypes
from html import unescape
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

from django.http import FileResponse, Http404, HttpRequest
from django.http.response import HttpResponseBase
from django.urls import reverse
from django.utils.html import strip_tags
from django.views.generic import TemplateView
from mvp.views.base import PageMixin

from mvp_sphinx.docs_build import DocsBuild

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
        """Serve the image or download, or render the page, at the requested address.

        Args:
            request: The request being served.
            *args: Positional URL arguments, unused.
            **kwargs: URL arguments; ``path`` is the address below the app's prefix.

        Returns:
            The file, or the rendered page.

        Raises:
            Http404: The docs build has no file or page at that address.
        """
        build = DocsBuild(self.app.build_dir)
        path = kwargs.get("path", "")
        target = build.file(path)
        if target is not None:
            content_type, _encoding = mimetypes.guess_type(target.name)
            return FileResponse(
                target.open("rb"),
                content_type=content_type or "application/octet-stream",
            )
        page = build.page(path)
        if page is None:
            raise Http404
        self.page_data = page
        return self.render_to_response(self.get_context_data(page_data=page))

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
        return self.plain_text(self.page_data["title"])

    def get_breadcrumbs(self) -> list[dict[str, Any]]:
        """Return the trail from the app's front page down to this page.

        The front page's trail is the app's name alone. On any other page the
        app's name links to the front page, each parent links to its own page,
        and the page itself has no link.
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
