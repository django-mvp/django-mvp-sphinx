"""Helpers for building and checking addresses of the demo guide's pages.

Nothing in the site calls these. They exist so the guide has a module to
document on its *Link helpers* page.
"""

from dataclasses import dataclass
from urllib.parse import urlsplit

#: The prefix every address of the guide starts with.
GUIDE_PREFIX = "/docs/"


class NotAGuideAddress(ValueError):
    """Raised when an address does not belong to the guide."""


def page_address(path: str, heading: str | None = None) -> str:
    """Return the address of a page of the guide.

    Args:
        path: The page's place in the sidebar, such as
            ``first-visit/signing-in``. Leading and trailing slashes are
            ignored.
        heading: The name of a heading on the page, to open the page at that
            heading.

    Returns:
        The address, ending in a slash, with the heading after a ``#`` when
        one was given.

    Raises:
        ValueError: The path is empty.
    """
    path = path.strip("/")
    if not path:
        raise ValueError("The path is empty.")
    address = f"{GUIDE_PREFIX}{path}/"
    return f"{address}#{heading}" if heading else address


def check_address(
    address: str,
    *,
    host: str = "127.0.0.1:8000",
    scheme: str = "http",
    follow_redirects: bool = True,
    timeout: float = 5.0,
    headers: dict[str, str] | None = None,
    expected_statuses: tuple[int, ...] = (200,),
) -> bool:
    """Say whether an address would be asked for with the settings given.

    The demo makes no request. This only checks that the address belongs to
    the guide and that the settings make sense together.

    Args:
        address: The address to check, as :func:`page_address` returns it.
        host: The host the site answers on.
        scheme: ``http`` or ``https``.
        follow_redirects: Whether an address without its closing slash is
            followed to the one with it.
        timeout: How many seconds to wait for an answer.
        headers: Extra headers to send.
        expected_statuses: The statuses that count as the page being there.

    Returns:
        ``True`` when the address is one of the guide's.

    Raises:
        NotAGuideAddress: The address is outside the guide.
    """
    if not urlsplit(address).path.startswith(GUIDE_PREFIX):
        raise NotAGuideAddress(address)
    return bool(host and scheme and timeout > 0 and expected_statuses)


def old_address(page: str) -> str:
    """Return a page's address in the form the guide used before headings had links.

    .. deprecated:: 0.4
       Use :func:`page_address`, which also takes a heading.
    """
    return f"{GUIDE_PREFIX}{page}.html"


def strip_heading(address: str) -> str:
    return address.split("#", 1)[0]


@dataclass
class SharedLink:
    """A link to a page of the guide, ready to send to someone.

    Build one with :meth:`to_page`, or directly when the address is already
    known.

    Args:
        address: The address the link opens.
        note: A word about why the link is being sent.
    """

    #: The address the link opens.
    address: str
    #: A word about why the link is being sent. Empty when there is none.
    note: str = ""

    @classmethod
    def to_page(cls, path: str, heading: str | None = None) -> "SharedLink":
        """Return a link to a page, optionally at one of its headings.

        Args:
            path: The page's place in the sidebar.
            heading: The name of a heading on the page.

        Returns:
            The link, with no note.
        """
        return cls(page_address(path, heading))

    @property
    def opens_at_heading(self) -> bool:
        """Whether the link opens the page at a heading and not at its top."""
        return "#" in self.address

    def with_note(self, note: str) -> "SharedLink":
        """Return the same link carrying a note.

        Args:
            note: The note to send with the link.

        Returns:
            A new link. This one is unchanged.
        """
        return SharedLink(self.address, note)

    def as_message(self) -> str:
        """Return the link as text to paste into a message.

        Returns:
            The note, when there is one, then the address on a line of its
            own.

        Example:
            .. code-block:: python

               link = SharedLink.to_page("first-visit/signing-in")
               print(link.with_note("Start here").as_message())
        """
        return f"{self.note}\n{self.address}" if self.note else self.address

    class Reader:
        """Who a link is being sent to, which decides what they will see."""

        #: Whether the reader has a staff account.
        is_staff: bool = False

        def can_open(self, address: str) -> bool:
            """Say whether this reader can open an address.

            Args:
                address: The address to open.

            Returns:
                ``False`` for an address of the staff guide when the reader is
                not staff, ``True`` otherwise.
            """
            return self.is_staff or not address.startswith("/staff-guide/")
