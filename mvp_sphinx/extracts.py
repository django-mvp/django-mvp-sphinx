"""A page of the docs build, or one section of it, shown outside the documentation app.

Imports neither Sphinx nor docutils: serving reads only the docs build's text.
"""

from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser

from django.utils.html import strip_tags
from django.utils.safestring import SafeString


def plain_text(markup: str) -> str:
    """Return the text of a title Sphinx wrote as HTML.

    Args:
        markup: A title as it appears in a page's JSON, possibly with inline
            markup such as ``<code>``.

    Returns:
        The title's text, unescaped, ready for a template to escape.
    """
    return unescape(strip_tags(markup))


@dataclass(frozen=True)
class PageExtract:
    """What a page of a documentation app holds, ready to place in a template.

    It renders as its content, so it can be set as a view's ``page_info`` as it is.
    It is false when its content holds no text and no image, so ``extract or ""``
    gives a view an empty ``page_info``, which draws no info icon.

    Attributes:
        content: The page's body without its title, wrapped in the documentation
            app's content styles.
        title: The page's title as plain text.
        url: The page's address in the documentation app.
    """

    content: SafeString
    title: str
    url: str

    def __str__(self) -> str:
        return self.content

    def __html__(self) -> str:
        return self.content

    def __bool__(self) -> bool:
        return bool(strip_tags(self.content).strip()) or "<img" in self.content


class SectionFinder(HTMLParser):
    """Find where a page's content starts and ends in its body.

    The content is everything inside the page's first section after its first
    heading. Offsets are counted as ``BodyRewriter`` counts them, so they index
    the body as written.

    Attributes:
        start: The offset just after the end tag of the first heading, or ``None``
            when the body has none.
        end: The offset of the end tag of the section, or ``None`` when it never
            closes.

    Args:
        body: A page body as Sphinx wrote it.
    """

    HEADINGS = frozenset(["h1", "h2", "h3", "h4", "h5", "h6"])

    def __init__(self, body: str) -> None:
        super().__init__(convert_charrefs=False)
        self.body = body
        self.line_starts = [0]
        for line in body.split("\n")[:-1]:
            self.line_starts.append(self.line_starts[-1] + len(line) + 1)
        self.depth = 0
        self.in_heading = False
        self.start: int | None = None
        self.end: int | None = None
        self.feed(body)
        self.close()

    def position(self) -> int:
        """Return the offset in the body where the parser stands."""
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Count a section and note the first heading directly inside the first."""
        if tag == "section":
            self.depth += 1
        elif tag in self.HEADINGS and self.depth == 1 and self.start is None:
            self.in_heading = True

    def handle_endtag(self, tag: str) -> None:
        """Note where the heading ends and where the first section does."""
        if tag in self.HEADINGS and self.in_heading:
            self.in_heading = False
            self.start = self.body.index(">", self.position()) + 1
        elif tag == "section":
            if self.depth == 1 and self.end is None:
                self.end = self.position()
            self.depth -= 1
