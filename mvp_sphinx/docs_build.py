"""The docs build on disk, and the lookups that never leave it."""

import json
from pathlib import Path
from typing import Any


class DocsBuild:
    """The directory ``sphinx-build -b json`` wrote, read without Sphinx.

    Every lookup is confined to the build: the root is resolved once, and a
    candidate that resolves outside it is treated as absent, so a symlinked
    build directory works and an address cannot reach files beside it.

    Args:
        root: The directory ``sphinx-build -b json`` wrote to. It need not exist.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    def page(self, path: str) -> dict[str, Any] | None:
        """Return the data of the page served at ``path``, or ``None``.

        A page is served at a slash-terminated address: ``""`` is the front
        page, and ``"a/b/"`` is the index page of folder ``a/b`` if there is
        one, otherwise the page ``a/b``. ``"a/index/"`` and ``"index/"`` also
        resolve, though Sphinx never links them. An address without a trailing
        slash is not a page.

        Args:
            path: The address below the documentation app's prefix.

        Returns:
            The page's JSON as Sphinx wrote it, or ``None`` when there is no
            page at ``path`` inside the build.

        Raises:
            json.JSONDecodeError: The page's file exists but is not valid JSON.
        """
        if path == "":
            candidates = ["index.fjson"]
        elif path.endswith("/"):
            candidates = [f"{path}index.fjson", f"{path[:-1]}.fjson"]
        else:
            return None
        for candidate in candidates:
            target = self._contained_file(candidate)
            if target is not None:
                data: dict[str, Any] = json.loads(target.read_text(encoding="utf-8"))
                return data
        return None

    def _contained_file(self, relative: str) -> Path | None:
        """Return the file ``relative`` names inside the build, or ``None``.

        Args:
            relative: An address relative to the build root.

        Returns:
            The resolved path when it is a file inside the build, otherwise
            ``None``, including for an address the filesystem rejects.
        """
        try:
            target = (self.root / relative).resolve()
            if target.is_relative_to(self.root) and target.is_file():
                return target
        except (ValueError, OSError):
            pass
        return None
