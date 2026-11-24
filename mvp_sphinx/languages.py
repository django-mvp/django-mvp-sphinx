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
from django.conf.locale import LANG_INFO
from django.utils.translation import to_language

from mvp_sphinx.docs_build import DocsBuild

#: Sphinx's default for ``language`` when ``conf.py`` doesn't set one.
DEFAULT_LANGUAGE = "en"
#: Sphinx's default for ``locale_dirs``.
DEFAULT_LOCALE_DIRS = ["locales"]


class SphinxSource:
    """A Sphinx source directory, read for the languages it is written and translated in.

    ``conf.py`` is read as text, so nothing here imports Sphinx or runs the
    project's configuration. A setting that isn't a literal reads as unset.

    Args:
        source_dir: The directory holding ``conf.py``, or ``None`` when the
            documentation app doesn't say where its source is.
    """

    def __init__(self, source_dir: Path | None) -> None:
        self.source_dir = None if source_dir is None else Path(source_dir)

    def assignments(self) -> dict[str, ast.expr]:
        """Return the top-level names ``conf.py`` assigns, with the value of each.

        Returns:
            Each assigned name and the expression assigned to it last, or
            nothing when ``conf.py`` can't be read.
        """
        if self.source_dir is None:
            return {}
        try:
            tree = ast.parse((self.source_dir / "conf.py").read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError):
            return {}
        return {
            target.id: node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        }

    def value(self, name: str, default: Any) -> Any:
        """Return a setting ``conf.py`` assigns a literal to, or ``default``."""
        assigned = self.assignments().get(name)
        if assigned is None:
            return default
        try:
            return ast.literal_eval(assigned)
        except ValueError:
            return default

    @property
    def language(self) -> str:
        """The language the documentation is written in, as Sphinx names it.

        ``conf.py``'s ``language``, or English when it sets none.
        """
        return self.value("language", None) or DEFAULT_LANGUAGE

    def translations(self) -> list[str]:
        """Return the languages the source has translations for, as Sphinx names them.

        A translation is a ``<locale_dir>/<language>/LC_MESSAGES`` folder
        holding at least one ``.po`` catalogue, under any of ``conf.py``'s
        ``locale_dirs``. Catalogues for the language the documentation is
        written in are corrections of the source, not a translation.

        Returns:
            The language codes, sorted.
        """
        if self.source_dir is None:
            return []
        source = to_language(self.language)
        found: set[str] = set()
        for locale_dir in self.value("locale_dirs", DEFAULT_LOCALE_DIRS) or []:
            root = self.source_dir / locale_dir
            if not root.is_dir():
                continue
            for folder in root.iterdir():
                messages = folder / "LC_MESSAGES"
                if (
                    to_language(folder.name) != source
                    and messages.is_dir()
                    and next(messages.rglob("*.po"), None)
                ):
                    found.add(folder.name)
        return sorted(found)


def site_languages() -> set[str]:
    """Return the project's ``LANGUAGES``, in Django's form (``pt-br``)."""
    return {to_language(code) for code, _name in settings.LANGUAGES}


class LanguageBuilds:
    """The language builds of a build directory, read from disk on every call.

    Args:
        build_dir: The build directory.
    """

    def __init__(self, build_dir: Path) -> None:
        self.build_dir = Path(build_dir)

    @staticmethod
    def is_language_build(folder: Path) -> bool:
        """Say whether a folder is a build of one language of the documentation.

        It holds a build and is named for a language Django knows or the
        project offers, so a build of something else kept beside them isn't
        taken for one.
        """
        return (
            folder.is_dir()
            and (folder / DocsBuild.CONTEXT_FILE).exists()
            and (
                to_language(folder.name) in LANG_INFO
                or to_language(folder.name) in site_languages()
            )
        )

    def builds(self) -> dict[str, Path]:
        """Return each language build, keyed in Django's form.

        The folders are listed on every call, so a language built while the
        site runs is served at once.

        Returns:
            The folder of each language build, by language (``pt-br`` for the
            folder ``pt_BR``). Nothing when the build directory holds a build
            of its own, or doesn't exist yet: it is then served as it is.
        """
        if (
            not self.build_dir.is_dir()
            or (self.build_dir / DocsBuild.CONTEXT_FILE).exists()
        ):
            return {}
        return {
            to_language(folder.name): folder
            for folder in sorted(self.build_dir.iterdir())
            if self.is_language_build(folder)
        }

    def build_for(self, language: str | None, source_dir: Path | None) -> Path:
        """Return the build that serves a reader of ``language``.

        Tried in turn: the language itself (``de-at``), its base language
        (``de``), the same two for ``LANGUAGE_CODE``, then the language the
        documentation is written in. The first build is the last resort, so a
        reader is served even where the source directory isn't there to name
        the language. The language is only ever looked up among the builds,
        never joined to the path.

        Args:
            language: Django's active language, or ``None`` when translation
                is turned off.
            source_dir: The Sphinx source directory, which names the language
                the documentation is written in.

        Returns:
            The build directory itself when it holds no language builds,
            otherwise the folder of the chosen language.
        """
        builds = self.builds()
        if not builds:
            return self.build_dir
        for code in (language, settings.LANGUAGE_CODE):
            if not code:
                continue
            code = to_language(code)
            for candidate in (code, code.partition("-")[0]):
                if candidate in builds:
                    return builds[candidate]
        source = to_language(SphinxSource(source_dir).language)
        return builds.get(source) or next(iter(builds.values()))
