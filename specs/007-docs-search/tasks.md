# Tasks — 007 Search the documentation

**Branch**: `007-docs-search` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. Documentation for a public name lands in the task
that introduces it. No test asserts wording, CSS classes, widths or placement (testing standard,
spec Assumptions); elements are found by landmark, role, accessible name, `href`, form `action`,
`method` and field `name`, and by the words and titles the fixture sources define.

Code standards for every task: no leading-underscore names anywhere (functions, methods, helpers,
constants, templates); line length 88; no compatibility aliases; Cotton components written as
`<c-…>` components, never through Cotton's template tags.

## Order

**US1 → (US2 + US3), sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — Find the pages that mention a word (P1)

Issue: #42. Delivers FR-001 – FR-009, FR-012, FR-014 (by reading on each search), FR-015; SC-001,
SC-002, SC-003, SC-004.

### T001 — `DocsSearch` finds the pages holding every word

**Files**: `mvp_sphinx/search.py`, `tests/sphinx/search/**`, `tests/conftest.py`,
`tests/test_search.py`, `pyproject.toml`, `uv.lock`

Plan, *The search* (everything except tiers, anchors and passages, which T003 adds; `results()`
here returns each match with `title`, `path`, `anchor=""`, `passage=""`, ordered by title then
document name); research R1–R4. Add `snowballstemmer>=2.2` to `[project] dependencies` (`uv lock`).
New source `tests/sphinx/search/` per plan *Fixtures and tests*, written in full now so T003 and
T004 need no new pages; `search_build` session fixture (builds with no warnings). Tests
(`TestDocsSearch`, on the real build unless said): each page's unique word lists that page only
(SC-001, US1.2); a word on several pages lists each once, with the right `path` (US1.3); two words
list only the pages holding both (US1.4); a different case and a different form (`lantern` /
`Lanterns`) find the page (US1.5); words in no page give `[]` (US1.6); `""`, spaces, only
punctuation give `[]` (US1.7); "the product list" finds the page with "product" and "list"
(edge case, stopwords); a word only in a page's file name gives `[]` (edge case); a fragment of a
word (`lante`) gives `[]` (FR-006); pure digits are ignored; no result's document is `genindex` or
`search` (edge case); for every plain lower-case key of `terms` and `titleterms`, searching the key
lists every document the data lists under it (SC-002, research R4); more than `WORD_LIMIT` words
does not raise (edge case). On files in `tmp_path` (copy the build): no `searchindex.json`, invalid
JSON, wrong shape each give `None`; a missing `language_data.js` still answers (a stopword alone
then finds nothing); `globalcontext.json` absent is read as English. Module and class docstrings per
`docs/contributing/standards/code-documentation.md`.

### T002 — The results page, and the search on every page

**Files**: `mvp_sphinx/views.py`, `mvp_sphinx/mounted.py`,
`mvp_sphinx/templates/mvp_sphinx/page.html`, `mvp_sphinx/templates/mvp_sphinx/search.html`,
`mvp_sphinx/templates/cotton/mvp_sphinx/search_form.html`, `tests/conftest.py`,
`tests/test_views.py`, `tests/test_mounted.py`, `tests/test_demo.py`,
`mvp_sphinx/locale/en/LC_MESSAGES/django.po`, `README.md`, `CHANGELOG.md`, `CONTEXT.md`

Plan, *The view*, *The URL*, *The form*, *The page and the results page*. In `page.html` add only
the form line (FS-003 rewrites this template in parallel). `search_app` fixture. Tests
(`TestSearchForm`, `TestSearchResults`, through `client`): every page of the app, the front page
included, carries a `form` with `role="search"`, `method="get"`, a field named `q`, and an `action`
that resolves to the app's `search` URL (FR-001, US1.1); the host's overview page has no such form
(FR-001); submitting — `GET` the form's `action` with `q` — answers 200 inside the shell and lists
the expected pages, each `href` under `/docs/` and resolving to a page that answers 200 (US1.2,
US1.3, FR-004); the same address requested twice gives the same list (US1.8); no match and an empty
`q` answer 200 with no result list, a `role="status"` element, and the form again with the query
filled in (US1.6, US1.7, FR-007); a query holding `<script>`, `"` and `&` comes back escaped in the
field and nowhere unescaped (US1.10, FR-008); the link in the fixture's front page to Sphinx's search
page, resolved against the page's address, is the app's `search` URL (US1.12, FR-009); a word only
in the host's overview page gives no result (US1.9, SC-003); `tests/test_mounted.py`: with the app's
`check` set to `False` (monkeypatch, restoring it), an anonymous `GET` of the search address is
refused exactly as a page address is (same status and redirect target) (FR-012). JavaScript off
(US1.11, FR-003) is covered by the `GET` form and server-side results; say so in the test class
docstring rather than writing a separate test. `tests/test_demo.py`: the demo's front page offers the
search. i18n: every string `{% trans %}`/`gettext_lazy`; `makemessages -l en`. README: under Usage,
a short "Search" subsection (what it searches, that it needs nothing configured, that it works with
scripts off). CHANGELOG Unreleased, Added: one entry. CONTEXT.md: "Search data" and "Results page"
(decisions D10), with the warning against "index" for the search data. Humanize README and
CHANGELOG text (public markdown).

---

## US2 — See which result is the right one (P2)

Issue: #43. Delivers FR-010, FR-011; FR-008 for titles and passages.

### T003 — Title matches first, a passage, and section links

**Files**: `mvp_sphinx/search.py`, `mvp_sphinx/templates/mvp_sphinx/search.html`,
`tests/test_search.py`, `tests/test_views.py`

Plan, *The search* (steps 3 and 5, `passage`, `PageText`). Tests (`TestResultOrder`,
`TestPassage`, `TestSectionLink`, `TestPageText`): "lantern" lists the page titled with it before
the pages that only mention it (US2.1, FR-010); a page matching in its title and body appears once
(edge case); each result's title is the page's title as plain text (US2.2); the passage holds the
searched word, carries no markup and no `¶`, and is at most about `PASSAGE_LENGTH` characters plus
the ellipses (US2.3); a passage for a stemmed match (`lanterns` in the page, `lantern` searched)
still finds the word; a word in a section heading makes that result's `href` end with the section's
anchor, which exists as an `id` in the page (US2.4); a title-only match has an empty passage or none
rendered; a page whose file is missing gives an empty passage, not an error; titles and passages
holding `<`, `&` render escaped (FR-008). `PageText`: skips `a.headerlink`, `script`, `style`;
converts entities.

---

## US3 — Search keeps up with the docs build (P3)

Issue: #44. Delivers FR-013, FR-014, FR-015; SC-005.

### T004 — Unavailable search, missing build, rebuild, two apps, no Sphinx

**Files**: `mvp_sphinx/views.py`, `mvp_sphinx/templates/mvp_sphinx/search.html`,
`tests/test_views.py`, `tests/conftest.py`, `mvp_sphinx/locale/en/LC_MESSAGES/django.po`

Plan, *The view* (`Http404` for a missing build, the unavailable state). Much of this is expected
to pass on first run where T002 already built it; that is not a red-step failure (the FS-002 T005
precedent). Tests (`TestSearchAfterARebuild`, `TestTwoApps`, `TestUnavailableSearch`,
`TestSearchWithoutSphinx`): build a copy of the search source into `tmp_path`, search a new word
(none), add a page holding it to the source and toctree, rebuild into the same output directory,
search again in the same process: listed (US3.1, FR-014); with `docs_app` on the search build and
`handbook_app` on the handbook build, a word common to both lists only the searched app's pages, all
under its own prefix (`/docs/` or `/manuals/admin/`) (US3.2); a copy of the build with
`searchindex.json` removed answers 200 with a `role="status"` element whose text differs from the
no-match one, and its pages still answer 200 (US3.3, FR-013, SC-005); the same with an invalid
`searchindex.json`; the handbook app while its build does not exist answers the search address
with the same status as one of its page addresses (US3.4); with Sphinx blocked in `sys.modules`
(the `TestServingWithoutSphinx` pattern) a search gives the same results (US3.5, FR-015, SC-004);
a query of 5,000 characters answers 200 (edge case).
