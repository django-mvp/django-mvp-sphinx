"""The languages a docs source is translated into, and the build that serves a reader.

A documentation source with translations is built once per language, each into
a folder of the build directory named for the language (``_build/json/de/``).
A source without translations is built straight into the build directory. The
layout on disk says which: a build directory holding a build of its own is
served as it is, and one that doesn't is served from its language folders.

Nothing here imports Sphinx. ``conf.py`` is read as text.
"""

import ast
from pathlib import Path
from typing import Any

from django.conf import settings
from django.utils.translation import to_language

#: Sphinx's default for ``language`` when ``conf.py`` doesn't set one.
DEFAULT_LANGUAGE = "en"
#: Sphinx's default for ``locale_dirs``.
DEFAULT_LOCALE_DIRS = ["locales"]


def conf_assignments(source_dir: Path) -> dict[str, ast.expr]:
    """Return the top-level names ``conf.py`` assigns, with the value of each.

    Args:
        source_dir: The Sphinx source directory, holding ``conf.py``.

    Returns:
        Each assigned name and the expression assigned to it last, or nothing
        when ``conf.py`` can't be read.
    """
    try:
        tree = ast.parse((Path(source_dir) / "conf.py").read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return {}
    return {
        target.id: node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }


def conf_value(source_dir: Path, name: str, default: Any) -> Any:
    """Return a setting ``conf.py`` assigns a literal to, or ``default``."""
    value = conf_assignments(source_dir).get(name)
    if value is None:
        return default
    try:
        return ast.literal_eval(value)
    except ValueError:
        return default


def source_language(source_dir: Path | None) -> str:
    """Return the language the documentation is written in, as Sphinx names it.

    Args:
        source_dir: The Sphinx source directory, or ``None`` when the
            documentation app doesn't say where it is.

    Returns:
        ``conf.py``'s ``language``, or English when it sets none.
    """
    if source_dir is None:
        return DEFAULT_LANGUAGE
    return conf_value(source_dir, "language", None) or DEFAULT_LANGUAGE


def translations(source_dir: Path) -> list[str]:
    """Return the languages the source has translations for, as Sphinx names them.

    A translation is a ``<locale_dir>/<language>/LC_MESSAGES`` folder holding
    at least one ``.po`` catalogue, under any of ``conf.py``'s ``locale_dirs``.

    Args:
        source_dir: The Sphinx source directory, holding ``conf.py``.

    Returns:
        The language codes, sorted.
    """
    locale_dirs = conf_value(source_dir, "locale_dirs", DEFAULT_LOCALE_DIRS)
    found: set[str] = set()
    for locale_dir in locale_dirs or []:
        root = Path(source_dir) / locale_dir
        if not root.is_dir():
            continue
        for language in root.iterdir():
            messages = language / "LC_MESSAGES"
            if messages.is_dir() and next(messages.rglob("*.po"), None):
                found.add(language.name)
    return sorted(found)


def site_languages() -> set[str]:
    """Return the project's ``LANGUAGES``, in Django's form (``pt-br``)."""
    return {to_language(code) for code, _name in settings.LANGUAGES}
