"""The rewrite that gives a page's body the attributes CSS cannot add."""

import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser

from django.utils.html import format_html, strip_tags
from django.utils.translation import gettext_lazy as _


@dataclass
class Equation:
    """Where the parts of an equation set out on its own line begin and end.

    Attributes:
        region_start: The offset the equation's notation begins at: just after
            its start tag, or after its number when the number is a direct child.
        number_start: The offset the number's content begins at, if it has one.
        number_link: The offset the number's heading link begins at, if it has one.
        number_end: The offset the number's end tag begins at, once it has closed.
    """

    region_start: int
    number_start: int | None = None
    number_link: int | None = None
    number_end: int | None = None


class BodyRewriter(HTMLParser):
    """Add to a page's body what CSS cannot, leaving every other byte as written.

    The parser only records where to insert markup, as offsets into the original
    string, and the result is that string with the insertions spliced in. Nothing
    it reads is re-emitted, so entity references, a bare ``&``, tag case and
    whitespace come back exactly as they arrived.

    It assumes well-formed HTML, which is what Sphinx writes. A table or an
    equation inside malformed raw HTML from a ``raw`` directive may be wrapped
    wrongly or not at all.

    It also notes whether the body holds maths: a start tag whose class list
    includes ``math``, which is how Sphinx marks both inline and displayed
    notation. Text inside a code sample is escaped, so it never counts.

    Every outermost ``<table>`` is wrapped in a named region that takes keyboard
    focus, so a table wider than the reading area scrolls sideways for a reader
    with no pointer. The region's name is the table's caption, or the word
    "Table" when it has none.

    Every equation set out on its own line (``div.math``) has its notation wrapped
    in the same kind of region, named "Equation" or, when numbered, "Equation"
    and the number as Sphinx wrote it, so a wide equation scrolls sideways for a
    reader with no pointer. The region opens after the number (``span.eqno``) when
    that is a direct child of the equation, so the number stays outside it, and
    otherwise straight after the equation's start tag. Inline maths is not
    wrapped.

    Every heading link (``a.headerlink``, which Sphinx puts on section headings,
    glossary terms and captions) is named for a screen reader: its ``title``, a
    colon and the text of the element that holds it, so each link on a page has
    a name of its own. A link with no ``title`` is named by the text alone. On a
    reference entry's signature (``dt.sig-object``) the text is the entry's own
    name and not the whole signature: its ``id`` when that is the full dotted name
    of the one ``sig-name`` it holds, otherwise the text of its ``sig-prename``
    and ``sig-name`` elements as written. An entry with no ``sig-name`` is named
    by the whole signature, as any other heading is.

    Args:
        markup: The body to read.
    """

    VOID_TAGS = frozenset(
        [
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "source",
            "track",
            "wbr",
        ]
    )

    def __init__(self, markup: str) -> None:
        super().__init__(convert_charrefs=False)
        self.markup = markup
        self.line_starts = [0]
        for line in markup.split("\n")[:-1]:
            self.line_starts.append(self.line_starts[-1] + len(line) + 1)
        self.insertions: list[tuple[int, str]] = []
        self.open_elements: list[tuple[str, int, list[str]]] = []
        self.entry_id: str | None = None
        self.entry_names: list[str] = []
        self.entry_parts: list[str] = []
        self.table_depth = 0
        self.table_start = 0
        self.caption_start: int | None = None
        self.caption_end: int | None = None
        self.has_maths = False
        self.equations: list[Equation] = []

    @classmethod
    def parse(cls, markup: str) -> "BodyRewriter":
        """Read the whole body and return the parser that holds what it found.

        Args:
            markup: A page body as Sphinx wrote it.

        Returns:
            The parser, closed, with ``has_maths`` set and every insertion
            recorded for ``splice``.
        """
        parser = cls(markup)
        parser.feed(markup)
        parser.close()
        return parser

    @classmethod
    def rewrite(cls, markup: str) -> str:
        """Return the body with its tables and heading links named.

        Args:
            markup: A page body as Sphinx wrote it.

        Returns:
            The same markup with each insertion spliced in.
        """
        return cls.parse(markup).splice()

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
        return self.text_between(self.caption_start, self.caption_end)

    def text_between(self, start: int, end: int) -> str:
        """Return the text of part of the markup as a reader would see it.

        Args:
            start: The offset the part begins at.
            end: The offset the part ends at.

        Returns:
            The part with tags removed, entities decoded and whitespace
            collapsed.
        """
        text = unescape(strip_tags(self.markup[start:end]))
        return re.sub(r"\s+", " ", text).strip()

    def entry_name(self) -> str:
        """Return the name of the reference entry whose signature is open.

        Returns:
            The entry's ``id`` when it holds one ``sig-name`` and the ``id``
            equals its text or ends with a dot and its text. Otherwise the text
            of its ``sig-prename`` and ``sig-name`` elements as written, or an
            empty string when it has no ``sig-name``.
        """
        if not self.entry_names:
            return ""
        if len(self.entry_names) == 1 and self.entry_id:
            name = self.entry_names[0]
            if self.entry_id == name or self.entry_id.endswith(f".{name}"):
                return self.entry_id
        return re.sub(r"\s+", " ", "".join(self.entry_parts)).strip()

    def in_equation(self) -> bool:
        """Return whether the innermost open element is an equation's ``div``."""
        if not self.open_elements:
            return False
        tag, classes = self.open_elements[-1][0], self.open_elements[-1][2]
        return tag == "div" and "math" in classes

    def end_number(self, content: int) -> None:
        """Move the region's start to after the number that is closing.

        Args:
            content: The offset the closing element's content began at.
        """
        equation = self.equations[-1]
        if equation.number_start != content or equation.number_end is not None:
            return
        start = self.position()
        equation.number_end = start
        equation.region_start = self.markup.index(">", start) + 1

    def end_equation(self) -> None:
        """Record the region around the notation of the equation that is closing."""
        equation = self.equations.pop()
        number = ""
        if equation.number_start is not None and equation.number_end is not None:
            stop = equation.number_link or equation.number_end
            number = self.text_between(equation.number_start, stop)
        label = str(_("Equation"))
        if number:
            label = str(_("Equation %(number)s")) % {"number": number}
        opening = format_html(
            '<div class="mvp-sphinx-scroll" role="region" tabindex="0" '
            'aria-label="{}">',
            label,
        )
        self.insertions.append((equation.region_start, opening))
        self.insertions.append((self.position(), "</div>"))

    def note_number_link(self) -> None:
        """Note where the heading link in an equation's number begins."""
        if not (self.equations and self.open_elements):
            return
        equation = self.equations[-1]
        holder_content = self.open_elements[-1][1]
        if equation.number_start == holder_content and equation.number_link is None:
            equation.number_link = self.position()

    def note_equation_end(self, index: int) -> None:
        """Close the equation or number whose element ends here.

        Args:
            index: The position in ``open_elements`` of the element being closed.
        """
        tag, content, classes = self.open_elements[index]
        if tag == "span" and "eqno" in classes and self.equations:
            self.end_number(content)
        elif tag == "div" and "math" in classes:
            for held in self.open_elements[index + 1 :]:
                if held[0] == "div" and "math" in held[2]:
                    self.equations.pop()
            self.end_equation()

    def name_heading_link(self, title: str | None) -> None:
        """Record an ``aria-label`` for the heading link starting here.

        Args:
            title: The link's ``title`` attribute, if it has one.
        """
        start = self.position()
        holder_start = self.open_elements[-1][1] if self.open_elements else start
        tag, holder = "", []
        if self.open_elements:
            tag, holder = self.open_elements[-1][0], self.open_elements[-1][2]
        is_entry = tag == "dt" and "sig-object" in holder
        entry_name = self.entry_name() if is_entry else ""
        text = entry_name or self.text_between(holder_start, start)
        label = ": ".join(part for part in (title, text) if part)
        if label:
            self.insertions.append(
                (start + len("<a"), format_html(' aria-label="{}"', label))
            )

    def note_entry_part(self, content: int, classes: list[str]) -> None:
        """Keep the text of a name in a signature as the element closes.

        Args:
            content: The offset the closing element's content began at.
            classes: Its class list.
        """
        in_signature = any("sig-object" in held for _, _, held in self.open_elements)
        if in_signature and ("sig-name" in classes or "sig-prename" in classes):
            text = unescape(strip_tags(self.markup[content : self.position()]))
            self.entry_parts.append(text)
            if "sig-name" in classes:
                self.entry_names.append(text.strip())

    def handle_starttag(self, tag, attrs):
        """Note where a table and its caption begin, and name a heading link."""
        attributes = dict(attrs)
        heading_link = (
            tag == "a" and "headerlink" in (attributes.get("class") or "").split()
        )
        classes = (attributes.get("class") or "").split()
        if heading_link:
            self.name_heading_link(attributes.get("title"))
            self.note_number_link()
        direct_child = self.in_equation()
        if "math" in classes:
            self.has_maths = True
        if tag == "dt" and "sig-object" in classes:
            self.entry_id = attributes.get("id")
            self.entry_names = []
            self.entry_parts = []
        if tag not in self.VOID_TAGS:
            content = self.position() + len(self.get_starttag_text())
            self.open_elements.append((tag, content, classes))
            if tag == "div" and "math" in classes:
                self.equations.append(Equation(region_start=content))
            elif tag == "span" and "eqno" in classes and direct_child:
                self.equations[-1].number_start = content
        if tag == "table":
            if self.table_depth == 0:
                self.table_start = self.position()
                self.caption_start = self.caption_end = None
            self.table_depth += 1
        elif self.table_depth == 1:
            if tag == "caption" and self.caption_start is None:
                self.caption_start = self.position() + len(self.get_starttag_text())
            elif (
                self.caption_start is not None
                and self.caption_end is None
                and heading_link
            ):
                self.caption_end = self.position()

    def handle_endtag(self, tag):
        """Wrap the outermost table once its end tag is read."""
        for index in range(len(self.open_elements) - 1, -1, -1):
            if self.open_elements[index][0] == tag:
                self.note_entry_part(*self.open_elements[index][1:])
                self.note_equation_end(index)
                del self.open_elements[index:]
                break
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
