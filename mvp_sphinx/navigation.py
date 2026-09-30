"""The Sphinx extension that writes the navigation file into a JSON build.

Name it in the host's ``conf.py``::

    extensions = ["mvp_sphinx.navigation"]

When ``sphinx-build -b json`` finishes, the extension walks every toctree from
the root document and writes the whole contents to ``navigation.json`` in the
docs build. The documentation app's sidebar is drawn from that file, so serving
never needs Sphinx. Other builders write nothing.

This is the only module of the package that imports Sphinx.
"""

import json
import os
from importlib.metadata import version
from pathlib import Path
from typing import Any

from sphinx import addnodes
from sphinx.application import Sphinx

from mvp_sphinx.docs_build import DocsBuild


class NavigationWriter:
    """Turn the toctrees of a finished JSON build into the navigation file.

    Args:
        app: The Sphinx application whose build has finished.
    """

    def __init__(self, app: Sphinx) -> None:
        self.env = app.env
        self.builder = app.builder
        self.root_doc = app.config.root_doc
        self.outdir = Path(app.outdir)

    def toctrees(self, docname: str) -> list[addnodes.toctree]:
        """Return the toctrees of one page, in document order, hidden ones too.

        Args:
            docname: The page's document name.

        Returns:
            The page's toctree nodes.
        """
        return list(self.env.get_doctree(docname).findall(addnodes.toctree))

    def entries(
        self, toctree: addnodes.toctree, path: tuple[str, ...]
    ) -> list[dict[str, Any]]:
        """Return the entries one toctree lists, each with its own pages below it.

        A page's own toctrees are flattened into its ``children``, and their
        captions are dropped. External links, ``self`` and pages missing from
        the build are left out, and so is a page already on the way down from
        the root, which is what ends a toctree that points back up the tree.

        Args:
            toctree: The toctree node to read.
            path: The document names from the root down to the page holding
                ``toctree``.

        Returns:
            One ``{"title", "url", "children"}`` mapping per entry.
        """
        entries = []
        for title, ref in toctree["entries"]:
            if ref not in self.env.titles or ref in path:
                continue
            below = (*path, ref)
            entries.append(
                {
                    "title": title or self.env.titles[ref].astext(),
                    "url": self.builder.get_target_uri(ref),
                    "children": [
                        entry
                        for nested in self.toctrees(ref)
                        for entry in self.entries(nested, below)
                    ],
                }
            )
        return entries

    def groups(self) -> list[dict[str, Any]]:
        """Return one group per toctree of the root document, in order.

        Returns:
            One ``{"caption", "entries"}`` mapping per toctree, with ``""`` as
            the caption of an uncaptioned one.
        """
        return [
            {
                "caption": toctree.get("caption") or "",
                "entries": self.entries(toctree, (self.root_doc,)),
            }
            for toctree in self.toctrees(self.root_doc)
        ]

    def write(self) -> None:
        """Write ``navigation.json`` into the build, replacing it in one step."""
        target = self.outdir / DocsBuild.NAVIGATION_FILE
        staging = target.with_name(f"{target.name}.tmp")
        staging.write_text(json.dumps({"groups": self.groups()}), encoding="utf-8")
        os.replace(staging, target)


def write_navigation(app: Sphinx, exception: Exception | None) -> None:
    """Write the navigation file once a JSON build has finished cleanly.

    Args:
        app: The Sphinx application.
        exception: The error that ended the build, or ``None``.
    """
    if exception is None and app.builder.name == "json":
        NavigationWriter(app).write()


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the extension with Sphinx.

    Args:
        app: The Sphinx application loading the extension.

    Returns:
        The extension's metadata.
    """
    app.connect("build-finished", write_navigation)
    return {
        "version": version("django-mvp-sphinx"),
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
