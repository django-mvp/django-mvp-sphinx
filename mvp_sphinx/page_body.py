"""What the package reads from a page's body before it is drawn."""

from html.parser import HTMLParser


class MathsFinder(HTMLParser):
    """Note whether a page body holds maths.

    Sphinx marks both inline and displayed notation with a start tag whose class
    list includes ``math``. Text inside a code sample is escaped, so it never
    counts.

    Attributes:
        found: Whether a start tag with the ``math`` class has been read.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.found = False

    def handle_starttag(self, tag, attrs):
        """Note a start tag whose class list includes ``math``."""
        if "math" in (dict(attrs).get("class") or "").split():
            self.found = True


def has_maths(markup: str) -> bool:
    """Say whether a page body holds maths.

    Args:
        markup: A page body as Sphinx wrote it.

    Returns:
        ``True`` when an element of the body has the ``math`` class.
    """
    finder = MathsFinder()
    finder.feed(markup)
    finder.close()
    return finder.found
