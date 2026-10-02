"""The contents of a docs build, as the menu its documentation app draws."""

import threading
from typing import TYPE_CHECKING, Any

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from flex_menu import Menu, MenuItem
from mvp.menus import MenuCollapse, MenuGroup

from mvp_sphinx.docs_build import DocsBuild

if TYPE_CHECKING:
    from django.http import HttpRequest

    from mvp_sphinx.mounted import DocumentationApp


class DocumentationMenu(Menu):
    """The contents of one documentation app, read from its navigation file.

    The menu starts with the front page, under its own title, then holds each
    captioned group of the contents as a group and each uncaptioned entry at the
    top level. A page with pages of its own opens as a collapsible group whose
    first entry is the page itself. Without a usable navigation file it holds
    the front page alone, and without a title in the file that entry reads
    "Overview".

    The menu is rebuilt only when the navigation file, the build directory or the
    app's front page address has changed since the last request.

    A project adds entries of its own with the menu's ``append``, ``extend`` and
    ``insert``. A rebuild replaces only what the navigation file put there. An
    entry placed ahead of the front page stays ahead of it, and every other entry
    follows the contents.

    Args:
        name: The menu's unique name.
        app: The documentation app whose docs build the menu shows.
    """

    def __init__(self, name: str, app: "DocumentationApp") -> None:
        super().__init__(name, children=[], extra_context={"label": app.name})
        self.app = app
        # Here from the start, so a project can place entries ahead of it.
        self.front_page = MenuItem(
            name="front-page",
            url=self.front_page_url,
            parent=self,
            extra_context={"label": _("Overview")},
        )
        self.contents: list[MenuItem] = []
        self.lock = threading.Lock()
        self.stamp: tuple[Any, ...] | None = None

    def front_page_url(self, request: "HttpRequest | None", **kwargs: Any) -> str:
        """Return the address the app's front page is served at."""
        return reverse(self.app.landing)

    def process(self, request: "HttpRequest", **kwargs: Any) -> MenuItem:
        """Bring the contents up to date, then process it for ``request``."""
        # Replacing the children is not atomic; see docs/adr/0002.
        with self.lock:
            self.refresh()
            return super().process(request, **kwargs)

    def refresh(self) -> None:
        """Rebuild the menu's items when the navigation file has changed."""
        prefix = reverse(self.app.landing)
        docs_build = DocsBuild(self.app.build_dir)
        stamp = (self.app.build_dir, prefix, docs_build.navigation_stamp())
        if stamp == self.stamp:
            return
        groups = docs_build.navigation() or []
        self.front_page.extra_context["label"] = docs_build.front_page_title() or _(
            "Overview"
        )
        contents: list[MenuItem] = []
        for number, group in enumerate(groups):
            entries = [
                self.entry_item(entry, prefix, f"g{number}-{position}")
                for position, entry in enumerate(group["entries"])
            ]
            if group["caption"]:
                contents.append(
                    MenuGroup(
                        name=f"g{number}",
                        extra_context={"label": group["caption"]},
                        children=entries,
                    )
                )
            else:
                contents += entries
        kept = [each for each in self if each not in self.contents]
        # A project may have taken the front page's entry out.
        after = kept.index(self.front_page) + 1 if self.front_page in kept else 0
        self.children = [*kept[:after], *contents, *kept[after:]]
        self.contents = contents
        self.stamp = stamp

    def entry_item(self, entry: dict[str, Any], prefix: str, name: str) -> MenuItem:
        """Return the menu item for one entry of the navigation file.

        Args:
            entry: The entry, as ``DocsBuild.navigation()`` returns it.
            prefix: The documentation app's own address, which every entry's
                address is below.
            name: The item's name, unique among its siblings.

        Returns:
            A link for a page without pages of its own, otherwise a collapsible
            group whose first item is the link to the page itself.
        """
        url = f"{prefix}{entry['url']}"
        if not entry["children"]:
            return MenuItem(name=name, url=url, extra_context={"label": entry["title"]})
        return MenuCollapse(
            name=name,
            extra_context={"label": entry["title"]},
            children=[
                MenuItem(
                    name=f"{name}-page",
                    url=url,
                    extra_context={"label": _("Overview")},
                ),
                *(
                    self.entry_item(child, prefix, f"{name}-{position}")
                    for position, child in enumerate(entry["children"])
                ),
            ],
        )
