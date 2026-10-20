"""The metadata tags of a page, read from the ``metatags`` Sphinx writes into its JSON."""

from html.parser import HTMLParser


class MetaTags(HTMLParser):
    """Read the ``<meta>`` tags of a page's ``metatags`` value into their attributes.

    Sphinx writes a page's metadata, from the ``meta`` directive or from MyST's
    ``html_meta`` front matter, as rendered ``<meta>`` tags. Reading them back into
    attributes lets the page template write them again through Django's escaping.
    """

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[dict[str, str]] = []

    @classmethod
    def from_markup(cls, markup: str) -> list[dict[str, str]]:
        """Return the attributes of every ``<meta>`` tag in the markup, in order.

        Args:
            markup: A page's ``metatags`` value, possibly empty.

        Returns:
            One dict per tag, mapping each attribute's name to its unescaped
            value. An attribute written without a value maps to an empty string.
        """
        parser = cls()
        parser.feed(markup)
        parser.close()
        return parser.tags

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Record a ``<meta>`` tag's attributes and ignore every other tag."""
        if tag == "meta":
            self.tags.append({name: value or "" for name, value in attrs})

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Read a self-closed tag, as Sphinx writes them, like any other."""
        self.handle_starttag(tag, attrs)
