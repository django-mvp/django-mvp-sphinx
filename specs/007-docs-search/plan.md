# Implementation Plan: Search the documentation

**Branch**: `007-docs-search` | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md) ·
**Research**: [research.md](research.md) · **Tasks**: [tasks.md](tasks.md)

## Summary

Sphinx's JSON build already writes its search data, `searchindex.json`, and its stopword list, in
`_static/language_data.js` (research R1, R3). A new `DocsSearch` class reads both from the docs
build on every search, turns the reader's words into the keys Sphinx stored them under (lower case,
then stemmed with the same snowball algorithm Sphinx used, R2), and lists the documents holding all
of them. Results come in three tiers: the words in the page's title, then in one of its section
headings (the result links to that section), then elsewhere. Each result carries a plain-text
passage cut from the page's own body. A `SearchView` serves the results page at `search/` under the
documentation app, which is exactly where Sphinx's own search page sits, so docs links to it land
here (FR-009). A small form component on every page of the app submits to it with `GET`, so it works
with JavaScript off and every search has an address. No Sphinx import; the one new runtime
dependency is `snowballstemmer`, the stemmer Sphinx itself uses.

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2 / 6.0 / 6.1

**Primary Dependencies**: django-mvp ≥ 0.25.0 (shell, `PageMixin`, `c-page`, `c-container`,
daisyUI classes in its stylesheet), django-cotton, **snowballstemmer ≥ 2.2** (new, runtime; see
Constitution Check VII). Standard library `html.parser`, `json`, `re`.

**Storage**: none. `searchindex.json`, `_static/language_data.js`, `globalcontext.json` and the
page `.fjson` files of the build are the only inputs, read on each search.

**Testing**: pytest + pytest-django; real Sphinx JSON builds from sources under `tests/sphinx/`,
session-scoped; pages requested through `client`.

**Performance Goals**: one parse of `searchindex.json` per search (tens to hundreds of kB for the
guides in scope) plus one page file per result for its passage. No cache (Article II; FR-014 wants
the build as it is on disk).

**Constraints**: serving never imports Sphinx (FR-015, Article XII); results only from this app's
build (FR-004); reader text and every title and passage escaped by the template layer (FR-008,
Article V); no reader rule of its own (FR-012).

**Scale/Scope**: guides of tens to a few hundred pages, all results on one page (D8); several
documentation apps per host.

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I Testing | Test-first per task; `DocsSearch` through a real build of a purpose-made source, the results page through `client`. JavaScript off (FR-003, US1.11) needs no test of its own: the form submits with `GET` and the results are rendered on the server, which is what every results-page test exercises. |
| II Simplicity | One class for search, one view, one template, one component. No settings, no cache, no JavaScript. |
| III Anti-abstraction | `DocsSearch` takes a `DocsBuild`; no base class, no backend interface. `PageText` subclasses the standard library's `HTMLParser`. |
| IV Integration-first | Acceptance tests submit the search the way a reader does (the form's `action`, `method` and field name, then `GET` that address) and read the results list by landmark and `href`. |
| V Security | The query, titles and passages are plain `str` rendered through `{{ }}`; nothing is marked safe. The query never reaches the filesystem: only fixed file names are read, plus page files named by the build's own `docnames`, through `DocsBuild`'s containment. |
| VI Documentation | README, CHANGELOG and CONTEXT.md in US1, where the search appears. |
| VII Dependencies | **`snowballstemmer`**, runtime. Justification: matching must stem words exactly as the build did (FR-006, SC-002), and the build stemmed with snowballstemmer. It is pure Python, has no dependencies, and is already installed wherever the docs are built, since Sphinx depends on it. Writing our own Porter/snowball port is the alternative, and it would drift. `deptry` sees it imported. |
| VIII i18n | Every visible string in the view, form and template is translatable; catalogue refreshed. |
| IX Data model | No models. |
| X Cohesion | Reading the search data, parsing a query, matching, ordering and cutting passages share one subject and sit on `DocsSearch`. The view's work is view methods. |
| XI Compatibility | New names only (`mvp_sphinx.search.DocsSearch`, `mvp_sphinx.search.PageText`, `mvp_sphinx.views.SearchView`, URL name `<namespace>:search`, component `mvp_sphinx.search_form`). Nothing removed or renamed. |
| XII Scope | Reads files of one build; no Sphinx import, no build, no second build. |
| XIII Host look | Results page extends `base.html` inside `c-page`/`c-container` like a page; the form uses daisyUI classes the shell emits; no Sphinx theme, no `searchtools.js`. |

Sam's standing code standards apply to every task: no leading-underscore names anywhere (methods,
helpers, templates, constants); line length 88; no compatibility aliases; no test of wording or
design preferences (layout, widths, placement); Cotton components written as `<c-…>` components,
never through Cotton's template tags.

No violations. Complexity tracking is empty.

## Design

### The search — `mvp_sphinx/search.py`

`class DocsSearch`: the search data of one docs build, read on each search.

- `SEARCH_DATA_FILE = "searchindex.json"`, `LANGUAGE_DATA_FILE = "_static/language_data.js"`,
  `CONTEXT_FILE = "globalcontext.json"`, `WORD_LIMIT = 20`, `PASSAGE_LENGTH = 240`.
- `ALGORITHMS`: language code → tuple of snowball algorithm names, from research R2:
  `{"en": ("english", "porter"), "da": ("danish",), "de": ("german",), ...}` for
  `da de es fi fr hu it nl no pt ro ru sv tr`. A language not listed gets no stemming beyond lower
  case; a missing or `null` language is read as `en`, as Sphinx does.
- `__init__(self, build: DocsBuild)`. Reads nothing yet.
- `data(self) -> dict | None`: `searchindex.json` through `build.contained_file`, parsed. `None`
  when absent, unreadable, not JSON, not UTF-8, or not the shape R1 describes (`docnames`, `titles`
  lists of the same length; `terms`, `titleterms` dicts). `alltitles` is optional (treated as `{}`).
  Never raises. **`None` is "search unavailable".**
- `stopwords(self) -> frozenset[str]`: the bracketed list after `stopwords` in
  `language_data.js` (regex `stopwords\s*=\s*(?:new Set\()?(\[[^\]]*\])`), JSON-parsed; empty when
  absent or unparsable (R3).
- `stemmers(self) -> list`: `snowballstemmer.stemmer(name)` for each algorithm of the language in
  `globalcontext.json`.
- `words(self, query: str) -> list[str]`: the query split on `[^\w]+`, lower-cased, stopwords and
  all-digit words dropped, duplicates dropped keeping order, cut to `WORD_LIMIT`.
- `keys(self, word: str) -> set[str]`: `{word}` plus each stemmer's stem of it (R2).
- `results(self, query: str) -> list[dict] | None`: `None` when `data()` is; otherwise the results,
  each `{"title": str, "path": str, "anchor": str, "passage": str}`:
  1. `words(query)`; none → `[]`.
  2. For each word, the documents holding any of its keys in `terms` ∪ `titleterms` (a value is an
     int or a list), with both mappings folded to lower case once per search, merging the documents
     of keys that differ only in case (Sphinx keeps a word as written when its stem is a stopword,
     so `Doing` is stored as `Doing`). A document is a match when it holds every word, with no
     exemption for short words (FR-005). Each document once (FR-004).
  3. Tier each match: 0 when every word has a key among the keys of the words of `titles[doc]`;
     1 when some section heading of the document in `alltitles` (anchor not `null`) holds every
     word the same way, and the first such heading's anchor becomes the result's `anchor`
     (FR-011); 2 otherwise. Sort by tier, then title case-insensitively, then document name
     (FR-010).
  4. `path`: the document's address below the app prefix — `""` for `index`, `a/` for `a/index`,
     `a/b/` for `a/b` (the inverse of `DocsBuild.page`).
  5. `passage(doc, word_keys)`.
- `passage(self, docname: str, word_keys: list[set[str]]) -> str`: the page file's `body` as plain
  text via `PageText`, whitespace collapsed; the first word (by `\w+` with positions) whose `keys()`
  meet any searched key; a window of about `PASSAGE_LENGTH` characters starting ~120 before it, cut
  at word boundaries, with "…" at a cut end. `""` when no word of the body matches or the page file
  cannot be read (`DocsBuild.page(path)` is `None` or raises `OSError` or `ValueError`). Never
  raises.

`class PageText(HTMLParser)`: the text a reader sees in a page body. Skips everything inside
`a.headerlink`, `script` and `style`; `@classmethod text(cls, markup) -> str`. The body is the
host's own build; entities are converted (`convert_charrefs=True`), so the result is plain text for
the template to escape.

### The view — `mvp_sphinx/views.py`

`class SearchView(PageMixin, TemplateView)`, `template_name = "mvp_sphinx/search.html"`,
`app` bound through `as_view(app=...)` like `PageView`.

- `get()`: `build = DocsBuild(self.app.build_dir)`; when `build.root` is not a directory → `Http404`
  (the same answer `PageView` gives every address of a missing build; FR-013, US3.4). Otherwise
  `query = request.GET.get("q", "")`, `results = DocsSearch(build).results(query)`, render with
  `query`, `results` (list, or `None` = unavailable), and each result's `href` resolved with
  `reverse(f"{namespace}:page", kwargs={"path": ...})` (front page for `""`) plus `#anchor`.
- `get_page_title()`: translatable "Search" (with the query when there is one).
- `get_breadcrumbs()`: the app's name linking to its front page, then "Search".

### The URL — `mvp_sphinx/mounted.py`

`DocumentationApp.__init__` binds `SearchView.as_view(app=self)` and `urls` gains
`path("search/", search_view, name="search")` **before** the
catch-all `<path:path>` pattern. Sphinx's own search page, `search.fjson`, is then no longer
reachable as a page, and every link a docs author makes to it lands on this search (FR-009, D4).
The mount's `check` wraps it like every other pattern (research R6; FR-012).

### The form — `mvp_sphinx/templates/cotton/mvp_sphinx/search_form.html`

Props: `action` (the results address), `query` (default empty), `label`. A `<form role="search"
method="get" action="{{ action }}">` with an accessible name, an `<input type="search" name="q">`
with a `<label>` (visually hidden) and the query as its value, and a submit button. daisyUI `join`,
`input input-sm`, `btn btn-sm` classes the shell's stylesheet emits. Annotated per
`docs/contributing/standards/code-documentation.md`.

### The page and the results page

- `mvp_sphinx/templates/mvp_sphinx/page.html`: one `<c-mvp_sphinx.search_form … />` line inside
  `c-container`, above the `<article>`. **Only that line changes**: FS-003 rewrites this template in
  parallel into a two-column layout, and a one-line insertion is what keeps the rebase trivial.
  `PageView.get_context_data` supplies the action URL (`reverse(f"{namespace}:search")`).
- `mvp_sphinx/templates/mvp_sphinx/search.html`: extends `base.html`, loads the same
  `content.css`; inside `c-page`/`c-container`: the form (query filled in), then one of three
  states:
  - results: a `<section>` labelled by a heading, holding an `<ol>`; each `<li>` an `<a href>` with
    the title and, when there is one, a `<p>` with the passage;
  - no results (empty query or no match): an element with `role="status"` saying nothing matched;
  - unavailable (`results is None`): an element with `role="status"` saying search is unavailable,
    in different words (FR-013).

### Fixtures and tests

- New source `tests/sphinx/search/` (`conf.py` with `mvp_sphinx.navigation` in `extensions`, like
  the other sources; builds with no warnings), pages designed for the scenarios:
  - `index.rst`: front page, toctree of the rest; a link to Sphinx's search page
    (`:ref:\`search\``), for FR-009.
  - each page carries one word no other page has (SC-001);
  - `lanterns.rst`: title holds "lanterns"; other pages mention "lantern" only in body text
    (US2.1, and a different form of the word, US1.5);
  - a page with a section heading holding a word the page's title and body lack elsewhere (US2.4);
  - two words each on several pages, both together on exactly one (US1.4);
  - a sentence "the product list" on one page (edge case, stopwords);
  - text with `<`, `&` and a quote (FR-008);
  - a page whose file name holds a word its text does not (edge case: addresses don't match);
  - a sub-folder with `index.rst` and a page, so results link to `a/` and `a/b/`.
- `tests/conftest.py`: `search_build` (session), `search_app` (points the demo app at it, the
  `contents_app` pattern).
- `tests/test_search.py`: `DocsSearch` and `PageText` directly on the real build and on files in
  `tmp_path` (malformed search data, missing stopword file).
- `tests/test_views.py`: `TestSearch…` classes through `client`.

### Demo

The demo guide gains nothing: its build already has search data, and its pages have enough words to
search. `tests/test_demo.py` gains one test that the demo's front page offers the search.

## Story order

US1 → US2 → US3, sequential in the feature worktree `wt-sphinx-007`. US1 is one dispatch (T001,
T002). US2 and US3 go out as one dispatch (T003, T004): US3 is mostly tests over code US1 wrote,
and one Implementer holding both avoids re-reading the same view.

## Project Structure

```text
mvp_sphinx/
├── search.py                                      # new: DocsSearch, PageText
├── views.py                                       # SearchView; PageView gains the search address
├── mounted.py                                     # the search/ pattern
├── templates/mvp_sphinx/page.html                 # one line: the form
├── templates/mvp_sphinx/search.html               # new
├── templates/cotton/mvp_sphinx/search_form.html   # new
└── locale/en/LC_MESSAGES/django.po                # refreshed
tests/
├── sphinx/search/**                               # new source
├── conftest.py                                    # search_build, search_app
├── test_search.py                                 # new
├── test_views.py                                  # results page
└── test_demo.py                                   # one test
pyproject.toml, uv.lock                            # snowballstemmer
README.md, CHANGELOG.md, CONTEXT.md
```

## Risks

- **Stemmer drift across Sphinx versions**: covered by looking a word up under every algorithm the
  language may have used (R2). A future Sphinx that changes algorithm again is a one-line change to
  `ALGORITHMS`.
- **Sibling features editing the same files** (FS-003 `page.html`, `views.py`; FS-006 tests and
  `conftest.py`): each change here is additive and small at the shared points, and the branch is
  rebased on main before S7 and whenever main moves.
