"""Search of a docs build, from the search data Sphinx writes into it."""

import json
import re
from functools import cached_property
from typing import Any

import snowballstemmer

from mvp_sphinx.docs_build import DocsBuild


class DocsSearch:
    """List the pages of a docs build that hold every word searched for.

    The build already carries what a search needs: ``searchindex.json`` records
    which pages hold which words, ``_static/language_data.js`` the words Sphinx
    left out as too common, and ``globalcontext.json`` the language it stemmed
    them in. Nothing is imported from Sphinx. The files are read when a search
    needs them and kept only for this instance's lifetime, so make one instance
    per search and a rebuilt docs build is seen by the next.

    Args:
        build: The docs build to search.
    """

    SEARCH_DATA_FILE = "searchindex.json"
    LANGUAGE_DATA_FILE = "_static/language_data.js"
    CONTEXT_FILE = "globalcontext.json"
    WORD_LIMIT = 20
    # Sphinx 9 stems English with the english algorithm, Sphinx 8 with porter.
    ALGORITHMS: dict[str, tuple[str, ...]] = {
        "en": ("english", "porter"),
        "da": ("danish",),
        "de": ("german",),
        "es": ("spanish",),
        "fi": ("finnish",),
        "fr": ("french",),
        "hu": ("hungarian",),
        "it": ("italian",),
        "nl": ("dutch",),
        "no": ("norwegian",),
        "pt": ("portuguese",),
        "ro": ("romanian",),
        "ru": ("russian",),
        "sv": ("swedish",),
        "tr": ("turkish",),
    }
    STOPWORDS_PATTERN = re.compile(r"stopwords\s*=\s*(?:new Set\()?(\[[^\]]*\])")

    def __init__(self, build: DocsBuild) -> None:
        self.build = build

    def read_json(self, name: str) -> Any:
        """Return the parsed JSON file ``name`` of the build, or ``None``.

        Args:
            name: The file's address relative to the build root.

        Returns:
            The parsed content, or ``None`` when the file is absent, unreadable,
            not valid UTF-8 or not JSON.
        """
        target = self.build.contained_file(name)
        if target is None:
            return None
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except (OSError, ValueError, RecursionError):
            return None

    def data(self) -> dict[str, Any] | None:
        """Return the build's search data, or ``None`` when it cannot be used.

        Returns:
            ``searchindex.json`` parsed, with ``docnames`` and ``titles`` lists of
            the same length, ``terms`` and ``titleterms`` mappings whose values are
            document numbers or lists of them, and ``alltitles`` a mapping
            (empty when the build has none). ``None`` when the file is absent,
            unreadable or not that shape, which callers report as search being
            unavailable.
        """
        data = self.read_json(self.SEARCH_DATA_FILE)
        if not isinstance(data, dict):
            return None
        docnames, titles = data.get("docnames"), data.get("titles")
        if not (
            isinstance(docnames, list)
            and isinstance(titles, list)
            and len(docnames) == len(titles)
            and all(isinstance(name, str) for name in docnames)
            and all(isinstance(title, str) for title in titles)
        ):
            return None
        for key in ("terms", "titleterms"):
            if not self.valid_postings(data.get(key), len(docnames)):
                return None
        if not isinstance(data.get("alltitles"), dict):
            data["alltitles"] = {}
        return data

    @staticmethod
    def valid_postings(postings: Any, count: int) -> bool:
        """Say whether ``postings`` maps words to documents that exist.

        Args:
            postings: A parsed ``terms`` or ``titleterms`` value.
            count: The number of documents in the build.

        Returns:
            ``True`` when every value is a document number or a list of them,
            each below ``count``.
        """
        if not isinstance(postings, dict):
            return False
        for value in postings.values():
            numbers = value if isinstance(value, list) else [value]
            for number in numbers:
                if (
                    not isinstance(number, int)
                    or isinstance(number, bool)
                    or not 0 <= number < count
                ):
                    return False
        return True

    @cached_property
    def stopwords(self) -> frozenset[str]:
        """The words the build left out of its search data as too common.

        Empty when the build has no language data file or it cannot be read.
        """
        target = self.build.contained_file(self.LANGUAGE_DATA_FILE)
        if target is None:
            return frozenset()
        try:
            match = self.STOPWORDS_PATTERN.search(target.read_text(encoding="utf-8"))
            words = json.loads(match.group(1)) if match else []
        except (OSError, ValueError):
            return frozenset()
        return frozenset(word for word in words if isinstance(word, str))

    @cached_property
    def stemmers(self) -> list[Any]:
        """The stemmers the build's language may have used, as Sphinx names them.

        A build that names no language is English, as it is to Sphinx. A
        language Sphinx has no stemmer for gets none.
        """
        context = self.read_json(self.CONTEXT_FILE)
        language = context.get("language") if isinstance(context, dict) else None
        code = language.lower() if isinstance(language, str) and language else "en"
        names = self.ALGORITHMS.get(code) or self.ALGORITHMS.get(
            code.partition("_")[0], ()
        )
        return [snowballstemmer.stemmer(name) for name in names]

    def words(self, query: str) -> list[str]:
        """Return the words of ``query`` that take part in a search.

        Args:
            query: What the reader typed.

        Returns:
            The lower-cased words, in order and each once, without the build's
            stopwords and without words made only of digits, cut to
            ``WORD_LIMIT``.
        """
        stopwords = self.stopwords
        words = dict.fromkeys(
            word
            for word in re.split(r"\W+", query.lower())
            if word and word not in stopwords and not word.isdecimal()
        )
        return list(words)[: self.WORD_LIMIT]

    def keys(self, word: str) -> set[str]:
        """Return the keys the search data may hold ``word`` under.

        Args:
            word: A lower-cased word from ``words()``.

        Returns:
            The word itself and its stem from each stemmer the build's language
            may have used.
        """
        return {word, *(stemmer.stemWord(word) for stemmer in self.stemmers)}

    def results(self, query: str) -> list[dict[str, str]] | None:
        """List the pages holding every word of ``query``.

        Args:
            query: What the reader typed.

        Returns:
            ``None`` when the build's search data cannot be used. Otherwise one
            mapping per matching page, ordered by title and then document name,
            with its ``title``, its ``path`` below the documentation app's
            prefix, and an ``anchor`` and ``passage`` that are empty. Empty
            when the query has no words or no page holds them all.
        """
        data = self.data()
        if data is None:
            return None
        words = self.words(query)
        if not words:
            return []
        postings: dict[str, set[int]] = {}
        for mapping in (data["terms"], data["titleterms"]):
            for key, value in mapping.items():
                numbers = value if isinstance(value, list) else [value]
                postings.setdefault(key.lower(), set()).update(numbers)
        matches: set[int] | None = None
        for word in words:
            found: set[int] = set()
            for key in self.keys(word):
                found |= postings.get(key.lower(), set())
            matches = found if matches is None else matches & found
            if not matches:
                return []
        docnames, titles = data["docnames"], data["titles"]
        ordered = sorted(
            matches or (),
            key=lambda number: (titles[number].lower(), docnames[number]),
        )
        return [
            {
                "title": titles[number],
                "path": self.path(docnames[number]),
                "anchor": "",
                "passage": "",
            }
            for number in ordered
        ]

    @staticmethod
    def path(docname: str) -> str:
        """Return the address below the app's prefix that serves ``docname``.

        The inverse of ``DocsBuild.page``.

        Args:
            docname: A document name from the search data, such as ``a/index``.

        Returns:
            ``""`` for the front page, ``"a/"`` for ``a/index`` and ``"a/b/"``
            for ``a/b``.
        """
        if docname == "index":
            return ""
        if docname.endswith("/index"):
            return docname[: -len("index")]
        return f"{docname}/"
