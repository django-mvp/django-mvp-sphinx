"""The rewrite that gives a page's body the attributes CSS cannot add."""

import re
from html import unescape
from html.parser import HTMLParser

from django.utils.html import format_html, strip_tags
from django.utils.translation import gettext_lazy as _


class BodyRewriter(HTMLParser):
    """Add to a page's body what CSS cannot, leaving every other byte as written.

    The parser only records where to insert markup, as offsets into the original
    string, and the result is that string with the insertions spliced in. Nothing
    it reads is re-emitted, so entity references, a bare ``&``, tag case and
    whitespace come back exactly as they arrived.

    Every outermost ``<table>`` is wrapped in a named region that takes keyboard
    focus, so a table wider than the reading area scrolls sideways for a reader
    with no pointer. The region's name is the table's caption, or the word
    "Table" when it has none.

    Args:
        markup: The body to read.
    """

    def __init__(self, markup: str) -> None:
        super().__init__(convert_charrefs=False)
        self.markup = markup
        self.line_starts = [0]
        for line in markup.split("\n")[:-1]:
            self.line_starts.append(self.line_starts[-1] + len(line) + 1)
        self.insertions: list[tuple[int, str]] = []
        self.table_depth = 0
        self.table_start = 0
        self.caption_start: int | None = None
        self.caption_end: int | None = None

    @classmethod
    def rewrite(cls, markup: str) -> str:
        """Return the body with its tables wrapped in named, focusable regions.

        Args:
            markup: A page body as Sphinx wrote it.

        Returns:
            The same markup with each insertion spliced in.
        """
        parser = cls(markup)
        parser.feed(markup)
        parser.close()
        return parser.splice()

    def position(self) -> int:
        """Return the offset in the markup where the parser stands."""
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def splice(self) -> str:
        """Return the markup with every recorded insertion applied.

        Returns:
            The original markup. Insertions at one offset keep the order they
            were recorded in.
        """
        pieces = []
        last = 0
        for offset, text in sorted(self.insertions, key=lambda item: item[0]):
            pieces.append(self.markup[last:offset])
            pieces.append(text)
            last = offset
        pieces.append(self.markup[last:])
        return "".join(pieces)

    def caption_text(self) -> str:
        """Return the text of the outermost table's caption, up to its link.

        Returns:
            The caption's text with tags removed, entities decoded and
            whitespace collapsed, or an empty string when there is none.
        """
        if self.caption_start is None or self.caption_end is None:
            return ""
        text = unescape(strip_tags(self.markup[self.caption_start : self.caption_end]))
        return re.sub(r"\s+", " ", text).strip()

    def handle_starttag(self, tag, attrs):
        """Note where a table and its caption begin and end."""
        if tag == "table":
            if self.table_depth == 0:
                self.table_start = self.position()
                self.caption_start = self.caption_end = None
            self.table_depth += 1
        elif self.table_depth == 1:
            if tag == "caption" and self.caption_start is None:
                self.caption_start = self.position() + len(self.get_starttag_text())
            elif self.caption_start is not None and self.caption_end is None:
                classes = (dict(attrs).get("class") or "").split()
                if tag == "a" and "headerlink" in classes:
                    self.caption_end = self.position()

    def handle_endtag(self, tag):
        """Wrap the outermost table once its end tag is read."""
        if tag == "caption" and self.table_depth == 1 and self.caption_end is None:
            self.caption_end = self.position()
        elif tag == "table" and self.table_depth:
            self.table_depth -= 1
            if self.table_depth == 0:
                label = self.caption_text() or str(_("Table"))
                opening = format_html(
                    '<div class="mvp-sphinx-scroll" role="region" tabindex="0" '
                    'aria-label="{}">',
                    label,
                )
                start = self.position()
                end = self.markup.index(">", start) + 1
                self.insertions.append((self.table_start, opening))
                self.insertions.append((end, "</div>"))
