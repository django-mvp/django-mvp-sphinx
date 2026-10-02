"""The ``live-example`` directive: a page of the site shown beside its source.

Registered by ``mvp_sphinx.navigation``, so the host's one line of Sphinx
configuration is all it needs::

    .. live-example:: /examples/contact/
       :title: A contact form

       ../../examples/forms.py
       ../../examples/views.py 12-30

The argument is an address of the host's own site. Each line of the content
names a source file, relative to the page's own file, and optionally the lines
of it to show. The files' text is written into the docs build, between comment
markers that ``mvp_sphinx.examples`` reads when the page is served.

This module imports Sphinx and is only loaded during a build.
"""

from pathlib import Path
from textwrap import dedent
from urllib.parse import quote, urlsplit

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

logger = logging.getLogger(__name__)


class LiveExample(SphinxDirective):
    """Write a live example's address and source into the page."""

    required_arguments = 1
    has_content = True
    option_spec = {"title": directives.unchanged}

    LANGUAGES = {".py": "python", ".html": "html+django", ".css": "css", ".js": "js"}

    def run(self) -> list[nodes.Node]:
        """Return the markers and one highlighted block per source file."""
        address = self.arguments[0]
        parts = urlsplit(address)
        if parts.scheme or parts.netloc or not address.startswith("/"):
            logger.warning(
                "live-example: %r is not an address of this site",
                address,
                location=self.get_location(),
            )
            return []
        sources = [block for line in self.content if (block := self.source(line))]
        if not sources:
            logger.warning(
                "live-example: %r names no source file that exists",
                address,
                location=self.get_location(),
            )
            return []
        title = self.options.get("title", "")
        result: list[nodes.Node] = [
            self.marker(
                f'mvp-live-example address="{quote(address, safe="/?=&")}" '
                f'title="{quote(title)}"'
            )
        ]
        for name, block in sources:
            result.append(self.marker(f'mvp-example-source name="{quote(name)}"'))
            result.append(block)
        result.append(self.marker("/mvp-live-example"))
        return result

    @staticmethod
    def marker(text: str) -> nodes.raw:
        """Return an HTML comment the served page is split on."""
        return nodes.raw("", f"<!--{text}-->", format="html")

    def source(self, line: str) -> tuple[str, nodes.literal_block] | None:
        """Return the name and highlighted text of one source line, or nothing."""
        if not line.strip():
            return None
        path, _, lines = line.strip().partition(" ")
        relative, absolute = self.env.relfn2path(path)
        self.env.note_dependency(relative)
        file = Path(absolute)
        if not file.is_file():
            logger.warning(
                "live-example: source file %s does not exist",
                path,
                location=self.get_location(),
            )
            return None
        text = file.read_text(encoding="utf-8")
        if lines.strip():
            first, _, last = lines.strip().partition("-")
            rows = text.splitlines()
            text = dedent("\n".join(rows[int(first) - 1 : int(last or first)]))
        block = nodes.literal_block(text, text)
        block["language"] = self.LANGUAGES.get(file.suffix, "text")
        return file.name, block
