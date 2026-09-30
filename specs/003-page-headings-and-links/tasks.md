# Tasks — 003 Show a page's headings beside it, and links to the previous and next page

**Branch**: `003-page-headings-and-links` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. Documentation for a public name lands in the task
that introduces it. No test asserts wording, CSS classes, widths or placement (testing standard,
spec Assumptions); elements are found by landmark, accessible name, `rel`, `href` and the ids and
titles the fixture sources define.

Code standards for every task: no leading-underscore names anywhere (functions, methods, helpers,
constants, templates, CSS); line length 88; no compatibility aliases; Cotton components written as
`<c-…>` components, never through Cotton's template tags.

## Order

**US1 → US2 → US3, one at a time, in the feature worktree** (plan, *Story order*). US2 and US3 are
one dispatch.

---

## US1 — Jump to a section of a long page (P1)

Issue: #34. Delivers FR-001 – FR-005, FR-011 (for the list); SC-001, SC-003.

### T001 — `PageHeadings` reads a page's heading tree

**Files**: `mvp_sphinx/headings.py`, `tests/sphinx/reading/**`, `tests/conftest.py`,
`tests/test_headings.py`

Plan, *The heading tree*; research R2. New source `tests/sphinx/reading/` per plan *Fixtures and
tests* (`conf.py` lists `mvp_sphinx.navigation`; builds with no warnings, so the session fixture's
assertion stands); `reading_build` session fixture. Tests (`TestPageHeadings`): on the real build,
the front page's tree holds its two sections in page order with the sub-section nested under the
second, and nothing from the pages its toctree lists (FR-001, FR-003); `long` nests three deep, each
entry's anchor is the `#id` of its heading in that page's `body` (FR-002); the inline-code heading's
title keeps its `<code>` markup (edge case); `single` gives one entry; `plain` gives `[]` (FR-004);
no entry anywhere is the page's own title. On plain fragments: `""` gives `[]`; a title holding an
empty `<ul>` gives `[]` (research R2); two outer entries give the first one's children followed by
the second. The title is a `SafeString` equal to the markup between the `<a …>` and `</a>` of the
fragment (plan: sliced, not re-emitted).

### T002 — "On this page" on the served page

**Files**: `mvp_sphinx/views.py`, `mvp_sphinx/templates/mvp_sphinx/page.html`,
`mvp_sphinx/templates/cotton/mvp_sphinx/on_this_page.html`,
`mvp_sphinx/templates/cotton/mvp_sphinx/heading_list.html`, `tests/conftest.py`,
`tests/test_views.py`, `mvp_sphinx/locale/en/LC_MESSAGES/django.po`

Plan, *The view* (`get_context_data`, `get_headings`), *The components* (the first two), *The
page*; research R4, R5. `reading_app` fixture. Do not edit `PageView.get()` or the `<article>`
element's content: FS-004 landed both; wrapping the article in the first column is expected. Tests (`TestOnThisPage`, through `client` on the reading build):
a page with sections carries a `nav` whose `aria-labelledby` names an element inside the page, and
its links are exactly that page's section anchors in page order (scenario 1); a sub-section's link
sits in a list nested inside its parent's `li` (scenario 2); every link's `href` is `#` + an `id`
present in the page's article (scenario 3); no link leads to `#` alone, the title (scenario 4);
`plain` has no such `nav` (scenario 5); the front page's list holds none of the anchors of the pages
it lists (scenario 6); the list's accessible name differs from the sidebar list's `aria-label`
(scenario 7, FR-005); the `single` page's list holds one link (edge case); with Sphinx blocked in
`sys.modules` (the `TestServingWithoutSphinx` pattern) the list is still drawn (FR-011). Components
annotated per `docs/contributing/standards/code-documentation.md`. `{% trans %}` for the name;
`makemessages -l en`.

### T003 — Demo guide, README and CHANGELOG for the list

**Files**: `demo/docs/settings.rst`, `README.md`, `CHANGELOG.md`

Plan, *Demo*. Settings gains one section; nothing else in the demo guide changes (the content
tour already has nested sections and an inline-code heading). README: under Usage, a short subsection saying pages list their own headings beside them on
wide screens, taken from the build with nothing to configure. CHANGELOG Unreleased, Added: one
entry written for someone deciding whether to upgrade. Humanize README text (public markdown).
`tests/test_demo.py` is unchanged unless a demo test breaks (then stop and report: it is not this
story's to edit).

---

## US2 — Carry on to the next page (P2)

Issue: #36. Delivers FR-006 – FR-009, FR-011 (for the links); SC-002.

### T004 — Previous and next links end every page

**Files**: `mvp_sphinx/views.py`, `mvp_sphinx/templates/mvp_sphinx/page.html`,
`mvp_sphinx/templates/cotton/mvp_sphinx/page_links.html`, `tests/test_views.py`,
`mvp_sphinx/locale/en/LC_MESSAGES/django.po`, `README.md`, `CHANGELOG.md`

Plan, *The view* (`get_neighbour`), *The components* (`page_links`), *The page*; research R3.
Tests (`TestPreviousAndNextPage`, through `client`): a middle page links to both, by `rel="prev"`
and `rel="next"`, inside a `nav` with an `aria-label` of its own, each link holding the title of the
page it leads to as the fixture source defines it (scenarios 1, 7); the front page has a next link
and no previous link (scenario 2); the last page has a previous link and no next (scenario 3); on
the page after the front page, the previous link leads to the app's own address, `/docs/`
(scenario 4); a build of a single page (a tiny source in `tmp_path`) has neither link (edge case);
starting
at the front page and following only next links visits every page the reading build lists, each
once, and ends on a page with no next link, and following previous links from there returns the same
way (SC-002); on `contents_app`, `hidden-page/` has both links and its neighbours link to it (edge
case) and `orphan/` has neither link and answers 200 (scenario 6); the handbook app mounted at
`manuals/admin/` links under its own prefix (scenario 5; `handbook_app` fixture; its two pages are
enough, do not edit that source); Sphinx's
general index page (`genindex/`) is served with neither link; with Sphinx blocked in
`sys.modules` the links are still drawn (FR-011). README: one paragraph beside T003's, including
one sentence that an incremental Sphinx build only rewrites changed pages and the pages whose
toctrees changed, so a page's previous and next links follow a newly inserted neighbour once that
page is rebuilt (a full rebuild, `-E`, if in doubt). CHANGELOG
entry. `{% trans %}` labels; `makemessages -l en`.

---

## US3 — A rebuilt docs build shows its new headings and order (P3)

Issue: #37. Delivers FR-010; SC-004.

### T005 — A rebuild shows on the next request

**Files**: `tests/test_views.py`, `tests/sphinx/reading/**` only if a page is needed

Research R1: the view reads the page file on every request, so this is expected to pass on first
run; that is not a red-step failure (the FS-002 T005 precedent). Tests
(`TestReadingAfterARebuild`): copy `tests/sphinx/reading/` into `tmp_path`, build it into an output
directory, point the demo app at it, request a page; add a section to that page's source and insert
a new page after it in its toctree, rebuild **into the same output directory**, request the same
page in the same process: the new section's anchor is in "On this page" (scenario 1) and the next
link leads to the inserted page (scenario 2). Use the `sphinx_build`-style fixture pattern in
`tests/conftest.py` (function-scoped, `tmp_path`).
