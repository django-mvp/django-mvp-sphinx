"""The languages a docs build is translated into, and the one that serves a reader.

A documentation source with translations is built once per language, each into
a folder of the build directory named for the language (``_build/json/de/``).
A source without translations is built straight into the build directory. The
layout on disk says which: a build directory holding a build of its own is
served as it is, and one that doesn't is served from its language folders.
"""

import ast
import threading
from functools import cache
from pathlib import Path
from typing import Any

from django.conf import settings
from django.utils.translation import to_language

#: The file every Sphinx JSON build writes, so a folder holding it is a build.
CONTEXT_FILE = "globalcontext.json"
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


@cache
def source_language(source_dir: Path | None) -> str:
    """Return the language the documentation is written in, as Sphinx names it."""
    if source_dir is None:
        return DEFAULT_LANGUAGE
    return conf_value(source_dir, "language", None) or DEFAULT_LANGUAGE


def translations(source_dir: Path) -> list[str]:
    """Return the languages the source has translations for, as Sphinx names them.

    A translation is a ``<locale_dir>/<language>/LC_MESSAGES`` folder holding
    at least one ``.po`` catalogue, under any of ``conf.py``'s ``locale_dirs``.
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


class BuildLanguages:
    """The language builds of each build directory, listed again when it changes."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.seen: dict[Path, tuple[int, dict[str, Path]]] = {}

    def builds(self, build_dir: Path) -> dict[str, Path]:
        """Return each language build in ``build_dir``, keyed in Django's form.

        Returns:
            Nothing when ``build_dir`` holds a build of its own, or doesn't
            exist yet: it is then served as it is.
        """
        build_dir = Path(build_dir)
        try:
            stamp = build_dir.stat().st_mtime_ns
        except OSError:
            return {}
        with self.lock:
            seen = self.seen.get(build_dir)
            if seen and seen[0] == stamp:
                return seen[1]
        if (build_dir / CONTEXT_FILE).exists():
            builds: dict[str, Path] = {}
        else:
            builds = {
                to_language(folder.name): folder
                for folder in sorted(build_dir.iterdir())
                if (folder / CONTEXT_FILE).exists()
            }
        with self.lock:
            self.seen[build_dir] = (stamp, builds)
        return builds

    def build_for(
        self, build_dir: Path, language: str | None, source_dir: Path | None
    ) -> Path:
        """Return the build that serves a reader of ``language``.

        Tried in turn: the language itself (``de-at``), its base language
        (``de``), the same two for ``LANGUAGE_CODE``, then the language the
        documentation is written in. The first build is the last resort.

        Args:
            build_dir: The build directory.
            language: Django's active language, or ``None`` when translation
                is turned off.
            source_dir: The Sphinx source directory, which names the language
                the documentation is written in.

        Returns:
            ``build_dir`` itself when it holds a build of its own, otherwise
            the folder of the chosen language.
        """
        builds = self.builds(build_dir)
        if not builds:
            return Path(build_dir)
        for code in (language, settings.LANGUAGE_CODE):
            if not code:
                continue
            code = to_language(code)
            for candidate in (code, code.partition("-")[0]):
                if candidate in builds:
                    return builds[candidate]
        source = to_language(source_language(source_dir))
        return builds.get(source) or next(iter(builds.values()))
