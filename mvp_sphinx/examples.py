"""Find the live examples the build wrote into a page's body.

Imports neither Sphinx nor docutils: serving reads only the docs build's text.
"""

from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlsplit

from django.urls import Resolver404, get_script_prefix, resolve
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe


class ExampleReader(HTMLParser):
    """Find where each example and each of its sources lies in a page's body.

    The reader counts ``div`` elements from each wrapper's opening to its
    matching close and records offsets, so the body can be sliced and what lies
    in a source passes through byte for byte.

    Attributes:
        examples: One dict per example whose wrapper closes, in page order, with
            ``start`` and ``end`` offsets in the body, the wrapper's attributes
            and ``sources``, each a dict with ``name`` and the offsets ``start``
            and ``end`` of what lies inside it.
    """

    def __init__(self, body: str) -> None:
        """Read a body.

        Args:
            body: A page body.
        """
        super().__init__(convert_charrefs=True)
        self.body = body
        self.lines = [0]
        for line in body.splitlines(keepends=True):
            self.lines.append(self.lines[-1] + len(line))
        self.depth = 0
        self.examples: list[dict[str, Any]] = []
        self.example: dict[str, Any] | None = None
        self.example_depth = 0
        self.source: dict[str, Any] | None = None
        self.source_depth = 0
        self.feed(body)
        self.close()

    def position(self) -> int:
        """Return the offset in the body of the tag being handled."""
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Treat a self-closed ``div`` as an opening, as a browser does."""
        self.handle_starttag(tag, attrs)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Count a ``div`` and begin an example or a source where one opens."""
        if tag != "div":
            return
        self.depth += 1
        values = dict(attrs)
        classes = (values.get("class") or "").split()
        if self.example is None:
            if LiveExamples.EXAMPLE_CLASS in classes:
                self.example = {
                    "start": self.position(),
                    "address": values.get(LiveExamples.ADDRESS_ATTRIBUTE) or "",
                    "title": values.get(LiveExamples.TITLE_ATTRIBUTE) or "",
                    "sources": [],
                }
                self.example_depth = self.depth
        elif self.source is None and LiveExamples.SOURCE_CLASS in classes:
            self.source = {
                "name": values.get(LiveExamples.NAME_ATTRIBUTE) or "",
                "start": self.position() + len(self.get_starttag_text() or ""),
            }
            self.example["sources"].append(self.source)
            self.source_depth = self.depth

    def handle_endtag(self, tag: str) -> None:
        """End the source or the example whose wrapper this ``div`` closes."""
        if tag != "div":
            return
        if self.source is not None and self.depth == self.source_depth:
            self.source["end"] = self.position()
            self.source = None
        elif self.example is not None and self.depth == self.example_depth:
            self.example["end"] = self.body.index(">", self.position()) + 1
            self.examples.append(self.example)
            self.example = None
        self.depth = max(self.depth - 1, 0)


class LiveExamples:
    """Split a page's body into its markup and the live examples between it.

    The ``live-example`` directive writes each example as a wrapper element
    around its sources. Reading them back needs no Sphinx, only the docs build's
    own text.
    """

    EXAMPLE_CLASS = "mvp-sphinx-example"
    SOURCE_CLASS = "mvp-sphinx-example-source"
    ADDRESS_ATTRIBUTE = "data-address"
    TITLE_ATTRIBUTE = "data-title"
    NAME_ATTRIBUTE = "data-name"

    @classmethod
    def parts(cls, body: str) -> list[dict[str, Any]]:
        """Return the body in order, as markup and examples.

        Args:
            body: A page body, already rewritten.

        Returns:
            Markup and examples alternating, starting and ending with markup,
            which is empty where an example opens or ends the body. Markup is
            ``{"html": ...}`` and an example is ``{"example": ...}``: a dict
            with ``id``, ``title``, ``address``, ``available`` and ``sources``,
            each source a dict with ``name`` and ``html``. A body without the
            example class is one markup part, unparsed. An example whose wrapper
            never closes stays in the markup.
        """
        if cls.EXAMPLE_CLASS not in body:
            return [{"html": mark_safe(body)}]  # noqa: S308
        parts: list[dict[str, Any]] = []
        last = 0
        for number, found in enumerate(ExampleReader(body).examples, start=1):
            # The body is the host's own docs build, trusted as it always was.
            parts.append({"html": mark_safe(body[last : found["start"]])})  # noqa: S308
            parts.append({"example": cls.example(body, number, found)})
            last = found["end"]
        parts.append({"html": mark_safe(body[last:])})  # noqa: S308
        return parts

    @classmethod
    def example(cls, body: str, number: int, found: dict[str, Any]) -> dict[str, Any]:
        """Return one example from where the reader found it.

        Args:
            body: The page body the reader read.
            number: The example's place in the page, counted from 1.
            found: One of the reader's examples.

        Returns:
            The example as ``parts`` describes it.
        """
        return {
            "id": f"{cls.EXAMPLE_CLASS}-{number}",
            "title": found["title"],
            "address": found["address"],
            "available": cls.available(found["address"]),
            "sources": [
                {
                    "name": source["name"],
                    "html": mark_safe(body[source["start"] : source["end"]]),  # noqa: S308
                }
                for source in found["sources"]
            ],
        }

    @staticmethod
    def available(address: str) -> bool:
        """Return whether the address is a page of this site that the site has.

        Args:
            address: An example's address.

        Returns:
            ``True`` when the address names this site and the current urlconf
            resolves its path, with the query, the fragment and the script
            prefix taken off. The page itself is never requested.
        """
        if not url_has_allowed_host_and_scheme(address, allowed_hosts=None):
            return False
        path = urlsplit(address).path
        prefix = get_script_prefix()
        if not path.startswith(prefix):
            return False
        try:
            resolve(path[len(prefix) - 1 :])
        except Resolver404:
            return False
        return True
