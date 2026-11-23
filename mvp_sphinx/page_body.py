"""What the package reads from a page's body before it is drawn."""

from html.parser import HTMLParser


def has_maths(markup: str) -> bool:
    """Say whether a page body holds maths.

    Sphinx marks both inline and displayed notation with a start tag whose class
    list includes ``math``. Text inside a code sample is escaped, so it never
    counts.

    Args:
        markup: A page body as Sphinx wrote it.

    Returns:
        ``True`` when an element of the body has the ``math`` class.
    """

    class Finder(HTMLParser):
        found = False

        def handle_starttag(self, tag, attrs):
            """Note a start tag whose class list includes ``math``."""
            if "math" in (dict(attrs).get("class") or "").split():
                self.found = True

    finder = Finder(convert_charrefs=False)
    finder.feed(markup)
    finder.close()
    return finder.found
