"""The contents of a docs build, as the menu its documentation app draws."""

import threading
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from flex_menu import Menu, MenuItem
from mvp.menus import MenuGroup

from mvp_sphinx.docs_build import DocsBuild

if TYPE_CHECKING:
    from django.http import HttpRequest

    from mvp_sphinx.mounted import DocumentationApp


class ContentsEntry(MenuItem):
    """One page of the contents, with the pages its toctrees list under it.

    The entry leads to its page, unless the page is hidden. The pages under it
    are drawn only while the entry is on the way to the page being read: on
    any other page the entry holds them back, and the sidebar fetches them from
    the entry's ``branch_url`` the first time a reader opens it.

    The pages are the entry's ``pages``, not its menu children, because a menu
    item with an address of its own can't hold children.

    ``extra_context`` carries the entry's ``label``, its ``page_url`` (set even
    when the page is hidden), its ``style``, its ``branch_url`` and ``entry``,
    the navigation file's mapping for the page with the pages under it.
    Processing adds ``current``, true on the entry's own page, ``branch``, true
    when it has pages under it, and ``open``, true when they are drawn.

    Args:
        pages: The entries for the pages listed under this one, in order.
        **kwargs: What a ``MenuItem`` takes.
    """

    def __init__(
        self, *args: Any, pages: list["ContentsEntry"] | None = None, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.pages = pages or []
        for page in self.pages:
            # A menu item with no parent joins the root menu; these belong here.
            page.parent = None
        self.addresses: set[str] = {
            self.normalized(self.extra_context["page_url"])
        }.union(*(page.addresses for page in self.pages))

    @staticmethod
    def normalized(path: str) -> str:
        """Return ``path`` without its trailing slash, to compare two addresses.

        Args:
            path: An address on the site.

        Returns:
            The address, ``/`` for the site's root.
        """
        return path.rstrip("/") or "/"

    def process(self, request: "HttpRequest", **kwargs: Any) -> MenuItem:
        """Select the entry on the way to the page being read, and open it there.

        Off that way, the processed entry holds no pages, so the sidebar draws
        the entry alone.

        Args:
            request: The request being served.
            **kwargs: What processing a menu item takes.

        Returns:
            The processed entry.
        """
        processed = super().process(request, **kwargs)
        if not processed.visible:
            return processed
        here = self.normalized(request.path)
        on_path = here in self.addresses
        processed.selected = on_path
        processed.pages = self.branch(request, **kwargs) if on_path else []
        processed.extra_context = {
            **processed.extra_context,
            "current": here == self.normalized(self.extra_context["page_url"]),
            "branch": bool(self.pages),
            "open": on_path and bool(self.pages),
        }
        return processed

    def branch(self, request: "HttpRequest", **kwargs: Any) -> list[MenuItem]:
        """Return the pages under this entry, processed for ``request``.

        Args:
            request: The request being served.
            **kwargs: What processing a menu item takes.

        Returns:
            The processed entries the reader may see, in order.
        """
        processed = (page.process(request, **kwargs) for page in self.pages)
        return [each for each in processed if each.visible]


class DocumentationMenu(Menu):
    """The contents of one documentation app, read from its navigation file.

    The menu starts with the front page, under its own title, then holds each
    captioned group of the contents as a group and each uncaptioned entry at the
    top level. Every page is a ``ContentsEntry``. The top entries are drawn on
    every page, and below them only the entries on the way to the page being
    read. A page whose ``menu_hidden`` is set has no link, and without pages of
    its own to show has no entry. Without a usable navigation file the menu
    holds the front page alone, and without a title in the file that entry reads
    "Overview".

    The menu is rebuilt only when the navigation file, the build directory or the
    app's front page address has changed since the last request. An app that
    chooses its build for each request rebuilds it whenever a request's build
    differs from the last one's.

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
        # The build directory of the request being processed, for refresh().
        self.build_dir: Any = None if callable(app.build_dir) else app.build_dir

    def front_page_url(self, request: "HttpRequest | None", **kwargs: Any) -> str:
        """Return the address the app's front page is served at."""
        return reverse(self.app.landing)

    def process(self, request: "HttpRequest", **kwargs: Any) -> MenuItem:
        """Bring the contents up to date, then process it for ``request``."""
        # Replacing the children is not atomic; see docs/adr/0002.
        with self.lock:
            self.build_dir = self.app.build_dir_for(request)
            self.refresh()
            return super().process(request, **kwargs)

    def branch(self, request: "HttpRequest", address: str) -> list[MenuItem] | None:
        """Return the pages under one entry, for a reader opening it in place.

        Args:
            request: The request being served.
            address: The entry's page address below the app's prefix, as the
                navigation file gives it.

        Returns:
            The entry's pages, processed for ``request``, or ``None`` when no
            entry with pages of its own has that address.
        """
        with self.lock:
            self.build_dir = self.app.build_dir_for(request)
            self.refresh()
            entries = list(self.contents)
            while entries:
                entry = entries.pop(0)
                if not isinstance(entry, ContentsEntry):
                    entries += entry.children
                elif entry.extra_context["entry"]["url"] == address and entry.pages:
                    return entry.branch(request)
                else:
                    entries += entry.pages
        return None

    def refresh(self) -> None:
        """Rebuild the menu's items when the navigation file has changed.

        It reads the build directory of the request being processed, which
        ``process`` sets in ``build_dir`` before calling it.
        """
        prefix = reverse(self.app.landing)
        docs_build = DocsBuild(self.build_dir)
        stamp = (self.build_dir, prefix, docs_build.navigation_stamp())
        if stamp == self.stamp:
            return
        groups = docs_build.navigation() or []
        self.front_page.extra_context["label"] = docs_build.front_page_title() or _(
            "Overview"
        )
        branch_url = reverse(f"{self.app.namespace}:branch")
        contents: list[MenuItem] = []
        for number, group in enumerate(groups):
            entries = self.entry_items(
                group["entries"], prefix, branch_url, f"g{number}"
            )
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

    def entry_items(
        self, entries: list[dict[str, Any]], prefix: str, branch_url: str, name: str
    ) -> list["ContentsEntry"]:
        """Return the menu entries for a list of entries of the navigation file.

        Args:
            entries: The entries, as ``DocsBuild.navigation()`` returns them.
            prefix: The documentation app's own address, which every entry's
                address is below.
            branch_url: The address the sidebar fetches an entry's pages from.
            name: The start of each entry's name, unique among the lists of
                entries.

        Returns:
            One entry per page that has something to show.
        """
        items = (
            self.entry_item(entry, prefix, branch_url, f"{name}-{position}")
            for position, entry in enumerate(entries)
        )
        return [item for item in items if item is not None]

    def entry_item(
        self, entry: dict[str, Any], prefix: str, branch_url: str, name: str
    ) -> "ContentsEntry | None":
        """Return the menu entry for one entry of the navigation file.

        Args:
            entry: The entry, as ``DocsBuild.navigation()`` returns it.
            prefix: The documentation app's own address, which every entry's
                address is below.
            branch_url: The address the sidebar fetches an entry's pages from.
            name: The entry's name, unique among its siblings.

        Returns:
            The entry, holding an entry for each page under it that has
            something to show. A hidden page has no link, and without pages of
            its own to show has no entry. An entry from a file written without
            these settings is neither hidden nor a group.
        """
        page_url = f"{prefix}{entry['url']}"
        hidden = entry.get("hidden", False)
        pages = self.entry_items(entry["children"], prefix, branch_url, name)
        if hidden and not pages:
            return None
        return ContentsEntry(
            name=name,
            url="" if hidden else page_url,
            pages=pages,
            extra_context={
                "label": entry["title"],
                "page_url": page_url,
                "style": entry.get("style", "collapse"),
                "branch_url": f"{branch_url}?{urlencode({'entry': entry['url']})}",
                "entry": entry,
            },
        )
