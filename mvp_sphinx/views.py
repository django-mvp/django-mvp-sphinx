"""The view that renders a page of the docs build."""

from typing import TYPE_CHECKING, Any

from django.http import Http404, HttpRequest, HttpResponse
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

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Render the page at the requested address, or answer not found.

        Args:
            request: The request being served.
            *args: Positional URL arguments, unused.
            **kwargs: URL arguments; ``path`` is the address below the app's prefix.

        Returns:
            The rendered page.

        Raises:
            Http404: The docs build has no page at that address.
        """
        page = DocsBuild(self.app.build_dir).page(kwargs.get("path", ""))
        if page is None:
            raise Http404
        self.page_data = page
        return self.render_to_response(self.get_context_data(page_data=page))
