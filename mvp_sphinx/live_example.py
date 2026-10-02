"""The ``live-example`` directive: a page of the site shown beside its source.

Registered by ``mvp_sphinx.navigation``, so the host's one line of Sphinx
configuration is all it needs::

    .. live-example:: /examples/contact/
       :title: A contact form

       ../../examples/forms.py
       ../../examples/views.py 12-30

The argument is an address of the host's own site. Each line of the content
names a source file, relative to the page's own file, and optionally the lines
of it to show.

The directive writes one element into the page's body, which
``mvp_sphinx.examples`` reads back when the page is served::

    <div class="mvp-sphinx-example" data-address="/examples/contact/"
         data-title="A contact form">
      <div class="mvp-sphinx-example-source" data-name="forms.py">
        <div class="highlight-python notranslate">...</div>
      </div>
      ...
    </div>

Each source's text is an ordinary highlighted code block, so a build read by
anything that does not know about examples shows plain code blocks.

This module imports Sphinx and is only loaded during a build.
"""

from html import escape
from pathlib import Path
from textwrap import dedent
from urllib.parse import urlsplit

from docutils import nodes
from docutils.parsers.rst import directives
from pygments.lexers import find_lexer_class_for_filename
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

from mvp_sphinx.examples import LiveExamples

logger = logging.getLogger(__name__)


class LiveExample(SphinxDirective):
    """Write a live example's address and source into the page."""

    required_arguments = 1
    has_content = True
    option_spec = {"title": directives.unchanged}

    # A Django project's .html files are templates, which Pygments reads as HTML.
    LANGUAGE_OVERRIDES = {".html": "html+django"}

    def run(self) -> list[nodes.Node]:
        """Return the example's wrapper around one highlighted block per source.

        Returns:
            The wrapper's opening, each source's opening, block and closing, and
            the wrapper's closing; nothing when the address is not of this site
            or no source file exists, after a warning.
        """
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
        result: list[nodes.Node] = [
            self.opening(
                LiveExamples.EXAMPLE_CLASS,
                {
                    LiveExamples.ADDRESS_ATTRIBUTE: address,
                    LiveExamples.TITLE_ATTRIBUTE: self.options.get("title", ""),
                },
            )
        ]
        for name, block in sources:
            result.append(
                self.opening(
                    LiveExamples.SOURCE_CLASS, {LiveExamples.NAME_ATTRIBUTE: name}
                )
            )
            result.append(block)
            result.append(self.closing())
        result.append(self.closing())
        return result

    @staticmethod
    def opening(class_name: str, attributes: dict[str, str]) -> nodes.raw:
        """Return the start of a wrapper element, its values escaped.

        Args:
            class_name: The wrapper's class.
            attributes: The wrapper's attributes and their values.

        Returns:
            A raw node for the HTML builders.
        """
        written = "".join(
            f' {name}="{escape(value)}"' for name, value in attributes.items()
        )
        return nodes.raw("", f'<div class="{class_name}"{written}>', format="html")

    @staticmethod
    def closing() -> nodes.raw:
        """Return the end of a wrapper element as a raw node."""
        return nodes.raw("", "</div>", format="html")

    def language(self, file: Path) -> str:
        """Return the language a file is highlighted as, by its name.

        Args:
            file: The source file.

        Returns:
            The override for its extension, else the first alias of the lexer
            Pygments has for its name, else ``text``.
        """
        if file.suffix in self.LANGUAGE_OVERRIDES:
            return self.LANGUAGE_OVERRIDES[file.suffix]
        lexer = find_lexer_class_for_filename(file.name)
        return lexer.aliases[0] if lexer else "text"

    def source(self, line: str) -> tuple[str, nodes.literal_block] | None:
        """Return the name and highlighted text of one source line, or nothing.

        Args:
            line: A content line: a file's path, then optionally its lines as
                ``first-last`` or one number.

        Returns:
            The file's name and a literal block of its text, or ``None`` for a
            blank line or a file that does not exist, the latter after a warning.
        """
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
        block["language"] = self.language(file)
        return file.name, block
