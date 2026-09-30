"""The heading tree of a page, read from the ``toc`` Sphinx writes into its JSON."""

from html.parser import HTMLParser
from typing import Any

from django.utils.safestring import mark_safe


class PageHeadings(HTMLParser):
    """Read a page's ``toc`` fragment into the tree of its headings.

    Sphinx writes the tree as nested lists whose single outer entry is the page's
    own title. Each entry holds one link, ``href="#<id>"``, and its sub-headings
    in a list of their own.

    A title is sliced out of the fragment by offset and never re-emitted, so its
    inline markup and entity references come back exactly as the build wrote
    them. It assumes Sphinx's own fragment, whose titles hold no nested link.

    Args:
        markup: The ``toc`` fragment to read.
    """

    def __init__(self, markup: str) -> None:
        super().__init__(convert_charrefs=False)
        self.markup = markup
        self.line_starts = [0]
        for line in markup.split("\n")[:-1]:
            self.line_starts.append(self.line_starts[-1] + len(line) + 1)
        self.outer: list[dict[str, Any]] = []
        self.open_lists: list[list[dict[str, Any]]] = []
        self.open_entries: list[dict[str, Any]] = []
        self.title_start: int | None = None

    @classmethod
    def from_toc(cls, toc: str) -> list[dict[str, Any]]:
        """Return the headings of a page, without the page's own title.

        Args:
            toc: A page's ``toc`` value, possibly empty.

        Returns:
            The headings below the title, each a dict with ``title`` (safe
            markup), ``anchor`` (``#<id>``) and ``children`` (the same, nested).
            A second outer entry, from a page with two top-level sections,
            follows the first one's children. A page with nothing below its
            title gives an empty list.
        """
        parser = cls(toc)
        parser.feed(toc)
        parser.close()
        if not parser.outer:
            return []
        title, *others = parser.outer
        return [*title["children"], *others]

    def position(self) -> int:
        """Return the offset in the markup where the parser stands."""
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def handle_starttag(self, tag, attrs):
        """Open a list, open an entry, or note where an entry's title begins."""
        if tag == "ul":
            if self.open_entries:
                self.open_lists.append(self.open_entries[-1]["children"])
            else:
                self.open_lists.append(self.outer)
        elif tag == "li" and self.open_lists:
            entry = {"title": "", "anchor": "", "children": []}
            self.open_lists[-1].append(entry)
            self.open_entries.append(entry)
        elif tag == "a" and self.open_entries and self.title_start is None:
            self.open_entries[-1]["anchor"] = dict(attrs).get("href") or ""
            self.title_start = self.position() + len(self.get_starttag_text())

    def handle_endtag(self, tag):
        """Close a list or an entry, or slice out the title that ends here."""
        if tag == "ul" and self.open_lists:
            self.open_lists.pop()
        elif tag == "li" and self.open_entries:
            self.open_entries.pop()
        elif tag == "a" and self.title_start is not None:
            # The build is the host's own output, trusted as the page body is.
            self.open_entries[-1]["title"] = mark_safe(  # noqa: S308
                self.markup[self.title_start : self.position()]
            )
            self.title_start = None
