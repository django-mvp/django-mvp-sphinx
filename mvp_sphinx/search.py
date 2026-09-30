"""Search of a docs build, from the search data Sphinx writes into it."""

import json
import re
from functools import cached_property
from html.parser import HTMLParser
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
    PASSAGE_LENGTH = 240
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
        # Passages stem every word of each result's page, and a page's
        # vocabulary repeats, so each word is stemmed once per search.
        self.stems: dict[str, set[str]] = {}

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
            if not all(DocsSearch.is_document(number, count) for number in numbers):
                return False
        return True

    @staticmethod
    def is_document(number: Any, count: int) -> bool:
        """Say whether ``number`` is the number of a document in the build.

        Args:
            number: A parsed value from the search data.
            count: The number of documents in the build.

        Returns:
            ``True`` for an integer, not a boolean, from 0 to below ``count``.
        """
        return (
            isinstance(number, int)
            and not isinstance(number, bool)
            and 0 <= number < count
        )

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
        if word not in self.stems:
            self.stems[word] = {
                word,
                *(stemmer.stemWord(word) for stemmer in self.stemmers),
            }
        return self.stems[word]

    def results(self, query: str) -> list[dict[str, str]] | None:
        """List the pages holding every word of ``query``, best match first.

        A page whose title holds every word comes first, then a page with a
        section heading that holds them all, then the rest. Within each of the
        three, pages are ordered by title and then document name.

        Args:
            query: What the reader typed.

        Returns:
            ``None`` when the build's search data cannot be used. Otherwise one
            mapping per matching page with its ``title``, its ``path`` below the
            documentation app's prefix, the ``anchor`` of the section holding the
            words (empty when the title or only the body does) and a ``passage``
            of the page around the first of them (empty when there is none).
            Empty when the query has no words or no page holds them all.
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
        word_keys = [{key.lower() for key in self.keys(word)} for word in words]
        matches: set[int] | None = None
        for keys in word_keys:
            found: set[int] = set()
            for key in keys:
                found |= postings.get(key, set())
            matches = found if matches is None else matches & found
            if not matches:
                return []
        docnames, titles = data["docnames"], data["titles"]
        sections = self.sections(data)
        ranked = []
        for number in matches or ():
            anchor = ""
            if self.holds(titles[number], word_keys):
                tier = 0
            else:
                anchor = next(
                    (
                        anchor
                        for heading, anchor in sections.get(number, ())
                        if self.holds(heading, word_keys)
                    ),
                    "",
                )
                tier = 1 if anchor else 2
            order = (tier, titles[number].lower(), docnames[number])
            ranked.append((order, number, anchor))
        return [
            {
                "title": titles[number],
                "path": self.path(docnames[number]),
                "anchor": anchor,
                "passage": self.passage(docnames[number], word_keys),
            }
            for number, anchor in (entry[1:] for entry in sorted(ranked))
        ]

    def holds(self, text: str, word_keys: list[set[str]]) -> bool:
        """Say whether the words of ``text`` cover every searched word.

        Args:
            text: A page title or a section heading.
            word_keys: The lower-cased keys of each searched word.

        Returns:
            ``True`` when each searched word has one of its keys among the keys
            of a word of ``text``.
        """
        held: set[str] = set()
        for word in re.findall(r"\w+", text.lower()):
            held |= {key.lower() for key in self.keys(word)}
        return all(keys & held for keys in word_keys)

    @staticmethod
    def sections(data: dict[str, Any]) -> dict[int, list[tuple[str, str]]]:
        """Return the section headings of each document, with their anchors.

        Args:
            data: The build's search data, from ``data()``.

        Returns:
            For a document number, its headings that have an anchor, each as the
            heading's text and the anchor. An entry that is not a pair of a
            document number below the document count and a non-empty anchor is
            left out.
        """
        count = len(data["docnames"])
        sections: dict[int, list[tuple[str, str]]] = {}
        for heading, entries in data["alltitles"].items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not (isinstance(entry, list) and len(entry) == 2):
                    continue
                number, anchor = entry
                if (
                    DocsSearch.is_document(number, count)
                    and isinstance(anchor, str)
                    and anchor
                ):
                    sections.setdefault(number, []).append((heading, anchor))
        return sections

    def passage(self, docname: str, word_keys: list[set[str]]) -> str:
        """Return the text of a page around the first searched word in it.

        Args:
            docname: A document name from the search data.
            word_keys: The lower-cased keys of each searched word.

        Returns:
            About ``PASSAGE_LENGTH`` characters of the page's text, cut at word
            boundaries with an ellipsis at each cut end. Empty when no word of
            the page's body matches, or when the page's file cannot be read.
        """
        try:
            page = self.build.page(self.path(docname))
        except (OSError, ValueError, RecursionError):
            return ""
        body = page.get("body") if isinstance(page, dict) else None
        if not isinstance(body, str):
            return ""
        text = PageText.text(body)
        searched = set().union(*word_keys)
        for hit in re.finditer(r"\w+", text):
            if self.keys(hit.group().lower()) & searched:
                break
        else:
            return ""
        start = max(0, hit.start() - self.PASSAGE_LENGTH // 2)
        if start:
            space = text.find(" ", start, hit.start())
            start = space + 1 if space != -1 else hit.start()
        end = min(len(text), start + self.PASSAGE_LENGTH)
        if end < len(text):
            space = text.rfind(" ", hit.end(), end)
            end = space if space != -1 else hit.end()
        head = "…" if start else ""
        tail = "…" if end < len(text) else ""
        return f"{head}{text[start:end]}{tail}"

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


class PageText(HTMLParser):
    """Collect the text a reader sees in the body of a page.

    The page's title (the ``h1`` Sphinx writes once, at the top of the body),
    Sphinx's permalinks, scripts and styles are left out, so a passage never
    just repeats the title the result already shows. Character references
    are converted, so the text is plain and a template is the one to escape it.
    """

    SKIPPED_TAGS = ("h1", "script", "style")

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skipping = ""
        self.depth = 0

    @classmethod
    def text(cls, markup: str) -> str:
        """Return the text of ``markup`` with its whitespace collapsed.

        Args:
            markup: A page's ``body`` as Sphinx wrote it.

        Returns:
            The text outside the title, permalinks, scripts and styles, in one line.
        """
        parser = cls()
        parser.feed(markup)
        parser.close()
        return " ".join("".join(parser.parts).split())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Start skipping at a permalink, script or style, or go deeper in one."""
        if self.skipping:
            self.depth += tag == self.skipping
        elif tag in self.SKIPPED_TAGS or (
            tag == "a" and "headerlink" in (dict(attrs).get("class") or "").split()
        ):
            self.skipping, self.depth = tag, 1

    def handle_endtag(self, tag: str) -> None:
        """Stop skipping when the element being skipped closes."""
        if self.skipping and tag == self.skipping:
            self.depth -= 1
            if not self.depth:
                self.skipping = ""

    def handle_data(self, data: str) -> None:
        """Keep the text that is not inside a skipped element."""
        if not self.skipping:
            self.parts.append(data)
