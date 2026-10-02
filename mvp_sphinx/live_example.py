"""The ``live-example`` directive: a page of the site shown beside its source.

Registered by ``mvp_sphinx.navigation``, so the host's one line of Sphinx
configuration is all it needs::

    .. live-example:: /examples/contact/
       :title: A contact form

       ../../examples/forms.py
       ../../examples/views.py 12-30

The argument is an address of the host's own site. Each line of the content
names a source file, relative to the page's own file or from the source
directory with a leading ``/``, and optionally the lines of it to show as
``first-last`` or one number, counted from 1. A source is named by its file,
with as many parent folders as tell it from another of the example, and with
its lines when the same file is named twice.

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

import re
from dataclasses import dataclass
from html import escape
from pathlib import Path
from textwrap import dedent

from docutils import nodes
from docutils.parsers.rst import directives
from pygments.lexers import find_lexer_class_for_filename
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

from mvp_sphinx.examples import LiveExamples

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Source:
    """One source of an example, as the author wrote it.

    Attributes:
        file: The file the source reads.
        lines: The lines written after the file, ``first-last`` or one number,
            or an empty string for the whole file.
        block: The highlighted text to show.
    """

    file: Path
    lines: str
    block: nodes.literal_block


class LiveExample(SphinxDirective):
    """Write a live example's address and source into the page."""

    required_arguments = 1
    final_argument_whitespace = True
    has_content = True
    option_spec = {"title": directives.unchanged}

    # The last word of a line is a range only when it has this shape, so a path
    # with spaces in it still reads as a path.
    LINES = re.compile(r"^(?P<path>.+?)\s+(?P<lines>\d+(?:-\d+)?)$")

    # One slash and then no host, backslash or whitespace: the shapes a browser
    # reads as another site (``//host/``, ``/\host/``) are all refused.
    ADDRESS = re.compile(r"/(?!/)[^\\\s]*")

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
        if not self.ADDRESS.fullmatch(address):
            logger.warning(
                "live-example: %r is not an address of this site",
                address,
                location=self.get_location(),
            )
            return []
        sources = [source for line in self.content if (source := self.source(line))]
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
        for name, source in zip(self.names(sources), sources, strict=True):
            result.append(
                self.opening(
                    LiveExamples.SOURCE_CLASS, {LiveExamples.NAME_ATTRIBUTE: name}
                )
            )
            result.append(source.block)
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

    @staticmethod
    def names(sources: list[Source]) -> list[str]:
        """Return the name each source is shown under, in the order given.

        Args:
            sources: The sources of one example.

        Returns:
            The file's name, with as many parent folders as tell it from every
            other file of the example, and its lines added when the same file is
            named more than once.
        """
        files = {source.file for source in sources}
        names = {}
        for file in files:
            others = files - {file}
            depth = 1
            while depth < len(file.parts) - 1 and any(
                other.parts[-depth:] == file.parts[-depth:] for other in others
            ):
                depth += 1
            names[file] = "/".join(file.parts[-depth:])
        times = [source.file for source in sources]
        return [
            f"{names[source.file]} {source.lines}"
            if source.lines and times.count(source.file) > 1
            else names[source.file]
            for source in sources
        ]

    def source(self, line: str) -> Source | None:
        """Return one source line read from its file, or nothing.

        Args:
            line: A content line: a file's path, then optionally its lines as
                ``first-last`` or one number.

        Returns:
            The source, or ``None`` for a blank line, a file that does not exist
            or a range that is not inside the file, the latter two after a
            warning naming the file.
        """
        line = line.strip()
        if not line:
            return None
        found = self.LINES.match(line)
        path, lines = (found["path"], found["lines"]) if found else (line, "")
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
        if lines:
            start, _, end = lines.partition("-")
            first, last = int(start), int(end or start)
            rows = text.splitlines()
            if not 1 <= first <= last <= len(rows):
                logger.warning(
                    "live-example: lines %s are not inside %s",
                    lines,
                    path,
                    location=self.get_location(),
                )
                return None
            text = dedent("\n".join(rows[first - 1 : last]))
        block = nodes.literal_block(text, text)
        block["language"] = self.language(file)
        return Source(file, lines, block)
