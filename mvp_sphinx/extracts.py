"""A page of the docs build, or one section of it, shown outside the documentation app."""

import logging
import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from typing import TYPE_CHECKING
from urllib.parse import urljoin, urlsplit

from django.http import HttpRequest
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html, strip_tags
from django.utils.safestring import SafeString, mark_safe

from mvp_sphinx.docs_build import DocsBuild
from mvp_sphinx.examples import LiveExamples
from mvp_sphinx.page_body import BodyRewriter

if TYPE_CHECKING:
    from mvp_sphinx.mounted import DocumentationApp

logger = logging.getLogger(__name__)

HEADINGS = frozenset(["h1", "h2", "h3", "h4", "h5", "h6"])
LINK_ATTRIBUTE = re.compile(r'(\s(?:href|src)=")([^"]*)(")')


@dataclass(frozen=True)
class PageExtract:
    """What a page, or one section of it, holds, ready to place in a template.

    It renders as its content, so it can be set as a view's ``page_info`` as it is.

    Attributes:
        content: The page's body without its title, or the section without its
            heading, wrapped in the documentation app's content styles.
        title: The page's title, or the section's heading, as plain text.
        url: The page's address in the documentation app, at the section when
            the extract is one.
    """

    content: SafeString
    title: str
    url: str

    def __str__(self) -> str:
        return self.content

    def __html__(self) -> str:
        return self.content


class SectionFinder(HTMLParser):
    """Find where a section's content starts and ends in a page's body.

    The content is everything inside the section after its heading. The section
    is the one with the given ``id``, or the body's first when no ``id`` is given.
    """

    def __init__(self, body: str, anchor: str) -> None:
        super().__init__(convert_charrefs=False)
        self.anchor = anchor
        self.line_starts = [0]
        for line in body.splitlines(keepends=True):
            self.line_starts.append(self.line_starts[-1] + len(line))
        self.depth = 0
        self.section_depth: int | None = None
        self.in_heading = False
        self.heading_text: list[str] = []
        self.title = ""
        self.start: int | None = None
        self.end: int | None = None
        self.feed(body)
        self.close()

    @property
    def position(self) -> int:
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag == "section":
            self.depth += 1
            if self.section_depth is None and (
                self.anchor == "" or dict(attrs).get("id") == self.anchor
            ):
                self.section_depth = self.depth
                self.start = -1
            return
        if self.start == -1 and tag in HEADINGS:
            self.in_heading = True
        elif self.in_heading and tag == "a" and "headerlink" in (
            dict(attrs).get("class") or ""
        ):
            self.in_heading = False

    def handle_endtag(self, tag):
        if self.start == -1 and tag in HEADINGS:
            self.title = unescape("".join(self.heading_text)).strip()
            self.in_heading = False
            # The content starts after the heading's end tag.
            self.start = self.rawdata.index(">", self.position) + 1
            return
        if tag == "section":
            if self.depth == self.section_depth and self.end is None:
                self.end = self.position
            self.depth -= 1

    def handle_data(self, data):
        if self.in_heading:
            self.heading_text.append(data)


def page_extract(
    app: "DocumentationApp", address: str, request: HttpRequest
) -> PageExtract | None:
    """Return a page of a documentation app, or one section of it, or ``None``.

    Args:
        app: The documentation app the page belongs to.
        address: The page's address below the app's prefix, such as
            ``"reference/accounts/"``, with ``#`` and a section's anchor to take
            only that section. The empty address is the front page.
        request: The request being served, for the app's reader rule.

    Returns:
        The extract, or ``None`` when the reader may not read the app, or the
        build, page or section is missing or broken.
    """
    if not app.has_permission(request):
        return None
    path, _, anchor = address.partition("#")
    try:
        page = DocsBuild(app.build_dir).page(path)
    except (OSError, ValueError):
        logger.warning("%s: the page at %r can't be read.", app.namespace, address)
        return None
    if page is None:
        logger.warning("%s: no page at %r.", app.namespace, address)
        return None
    body = page.get("body", "")
    found = SectionFinder(body, anchor)
    if found.start in (None, -1) or found.end is None:
        logger.warning("%s: no section at %r.", app.namespace, address)
        return None
    if path:
        page_url = reverse(f"{app.namespace}:page", kwargs={"path": path})
    else:
        page_url = reverse(f"{app.namespace}:front_page")
    markup = rewrite_links(body[found.start : found.end], page_url)
    rewritten = BodyRewriter.parse(markup).splice()
    # Live examples need the documentation app's own page around them.
    kept = "".join(
        str(part["html"]) for part in LiveExamples.parts(rewritten) if "html" in part
    )
    content = format_html(
        '<link rel="stylesheet" href="{}">'
        '<div class="prose mvp-sphinx-content mvp-sphinx-extract">{}</div>',
        static("mvp_sphinx/content.css"),
        mark_safe(kept),  # noqa: S308 the host's own docs build
    )
    title = found.title if anchor else unescape(strip_tags(page.get("title", "")))
    return PageExtract(
        content=content,
        title=title,
        url=f"{page_url}#{anchor}" if anchor else page_url,
    )


def rewrite_links(markup: str, page_url: str) -> str:
    """Point every relative link and image in ``markup`` at the documentation app."""

    def absolute(match: re.Match[str]) -> str:
        target = match.group(2)
        if urlsplit(target).scheme or target.startswith("/"):
            return match.group(0)
        return f"{match.group(1)}{urljoin(page_url, target)}{match.group(3)}"

    return LINK_ATTRIBUTE.sub(absolute, markup)

