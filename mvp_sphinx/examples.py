"""Find the live examples the build wrote into a page's body."""

import re
from typing import Any
from urllib.parse import unquote, urlsplit

from django.urls import Resolver404, resolve
from django.utils.safestring import mark_safe


class LiveExamples:
    """Split a page's body into its markup and the live examples between it.

    The ``live-example`` directive writes each example between comment markers.
    Reading them back needs no Sphinx, only the docs build's own text.
    """

    EXAMPLE = re.compile(
        r'<!--mvp-live-example address="([^"]*)" title="([^"]*)"-->'
        r"(.*?)<!--/mvp-live-example-->",
        re.DOTALL,
    )
    SOURCE = re.compile(r'<!--mvp-example-source name="([^"]*)"-->')
    # Prototype only: how a page knows it is being shown as an example.
    FRAMED = "example=1"

    @classmethod
    def parts(cls, body: str) -> list[dict[str, Any]]:
        """Return the body in order, as markup and examples.

        Args:
            body: A page body, already rewritten.

        Returns:
            One dict per part: ``{"html": ...}`` for markup and
            ``{"example": ...}`` for a live example.
        """
        parts: list[dict[str, Any]] = []
        last = 0
        for number, match in enumerate(cls.EXAMPLE.finditer(body), start=1):
            # The body is the host's own docs build, trusted as it always was.
            parts.append({"html": mark_safe(body[last : match.start()])})  # noqa: S308
            parts.append({"example": cls.example(number, match)})
            last = match.end()
        parts.append({"html": mark_safe(body[last:])})  # noqa: S308
        return parts

    @classmethod
    def example(cls, number: int, match: re.Match[str]) -> dict[str, Any]:
        """Return one example: its address, whether the site has it, its source."""
        address = unquote(match.group(1))
        pieces = cls.SOURCE.split(match.group(3))[1:]
        joiner = "&" if "?" in address else "?"
        return {
            "id": f"mvp-sphinx-example-{number}",
            "title": unquote(match.group(2)),
            "address": address,
            "framed_address": f"{address}{joiner}{cls.FRAMED}",
            "available": cls.available(address),
            "sources": [
                {"name": unquote(name), "html": mark_safe(html)}  # noqa: S308
                for name, html in zip(pieces[::2], pieces[1::2], strict=True)
            ],
        }

    @staticmethod
    def available(address: str) -> bool:
        """Return whether the site has a page at the address."""
        try:
            resolve(urlsplit(address).path)
        except Resolver404:
            return False
        return True
