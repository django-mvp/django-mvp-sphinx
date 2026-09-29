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

    FILE_FOLDERS = ("_images", "_downloads")
    NAVIGATION_FILE = "navigation.json"

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    def page(self, path: str) -> dict[str, Any] | None:
        """Return the data of the page served at ``path``, or ``None``.

        A page is served at a slash-terminated address: ``""`` is the front
        page, and ``"a/b/"`` is the index page of folder ``a/b`` if there is
        one, otherwise the page ``a/b``. Every page has that one address only:
        ``"index/"``, ``"a/index/"``, empty, ``.`` or ``..`` segments and
        absolute paths are not pages. An address without a trailing slash is
        not a page.

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
        elif path.endswith("/") and self.is_canonical(path[:-1]):
            if path[:-1].rsplit("/", 1)[-1] == "index":
                # The folder's own address serves its index page.
                return None
            candidates = [f"{path}index.fjson", f"{path[:-1]}.fjson"]
        else:
            return None
        for candidate in candidates:
            target = self.contained_file(candidate)
            if target is not None:
                data: dict[str, Any] = json.loads(target.read_text(encoding="utf-8"))
                return data
        return None

    def file(self, path: str) -> Path | None:
        """Return the image or download served at ``path``, or ``None``.

        Only ``_images/`` and ``_downloads/`` are ever files: the page data,
        search index, sources, static files and pickles beside them never are.
        The target must resolve inside its own folder, so ``_images/../x`` and a
        symlink pointing out of the folder are absent.

        Args:
            path: The address below the documentation app's prefix.

        Returns:
            The file's resolved path, or ``None`` when ``path`` is not a file
            inside one of the two folders.
        """
        folder = path.split("/", 1)[0]
        if folder not in self.FILE_FOLDERS or not self.is_canonical(path):
            return None
        return self.contained_file(path, within=folder)

    @staticmethod
    def is_canonical(relative: str) -> bool:
        """Say whether ``relative`` is a plain relative address.

        Args:
            relative: An address below the documentation app's prefix, without
                its trailing slash.

        Returns:
            ``False`` for an absolute path or one with an empty, ``.`` or ``..``
            segment, which would otherwise name the same file by a second
            address, or a path on the disk.
        """
        return not relative.startswith("/") and all(
            segment not in ("", ".", "..") for segment in relative.split("/")
        )

    def contained_file(self, relative: str, within: str = "") -> Path | None:
        """Return the file ``relative`` names inside the build, or ``None``.

        Args:
            relative: An address relative to the build root.
            within: A folder of the build the file must also sit in; the whole
                build when empty. The file must stay inside the build as well,
                even when the folder is a link to somewhere else.

        Returns:
            The resolved path when it is a file inside the build, otherwise
            ``None``, including for an address the filesystem rejects.
        """
        try:
            boundary = (self.root / within).resolve()
            target = (self.root / relative).resolve()
            inside = target.is_relative_to(self.root) and target.is_relative_to(
                boundary
            )
            if inside and target.is_file():
                return target
        except (ValueError, OSError):
            pass
        return None
