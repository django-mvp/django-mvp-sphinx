"""The sidebar renderer that draws the contents along the reader's path."""

from typing import Any

from flex_menu import MenuItem
from mvp.renderers import SidebarRenderer as MvpSidebarRenderer

from mvp_sphinx.menus import ContentsEntry


class SidebarRenderer(MvpSidebarRenderer):
    """django-mvp's sidebar renderer, drawing each page of the contents as well.

    Name it as the sidebar renderer in your settings::

        FLEX_MENUS = {
            "renderers": {
                "sidebar": "mvp_sphinx.renderers.SidebarRenderer",
            },
        }

    Every other item of every menu is drawn exactly as django-mvp draws it. A
    page of the contents is drawn by ``mvp_sphinx/contents/entry.html``: a link
    to the page and, for a page with pages of its own, a toggle that opens them
    in place. The script that fetches a closed branch and scrolls the page being
    read into view comes with the menu.
    """

    class Media:
        css = {"all": ("mvp_sphinx/contents.css",)}
        js = ("mvp_sphinx/contents.js",)

    def get_template(self, item: MenuItem) -> str:
        """Return the contents' entry template for a page of the contents."""
        if isinstance(item, ContentsEntry):
            return "mvp_sphinx/contents/entry.html"
        template: str = super().get_template(item)
        return template

    def get_context_data(self, item: MenuItem, **kwargs: Any) -> dict[str, Any]:
        """Add the request, which a project's own entry template may read."""
        return {**super().get_context_data(item, **kwargs), "request": item.request}
