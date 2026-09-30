# Progress — 003 Show a page's headings beside it, and links to the previous and next page

## 2026-09-30T00:40:00Z · S3 plan

Did: queue row for FS-003 read `in-flight` because the orchestrating session claimed it for this
run; no pull request built it yet. Features delivered since the spec landed (FS-001, FS-002) re-read
against it: no contradiction (D1). The old local spec branch was reset to origin/main (044ef54);
worktree `wt-sphinx-003`, identity bound. Baseline `forge verify` green on 044ef54. Planned from the
reviewed prototype (django-mvp `wip/sphinx-docs-in-sidebar`) without django-sphinx-view:
research.md (premises read from Sphinx 9.1.0, serializinghtml 2.0.0, django-mvp 0.25.0 as
installed), plan.md, tasks.md: 3 stories, 5 tasks. Decisions D1–D5 appended.
Analyze: FR-001–FR-011 and SC-001–SC-004 each map to at least one task; every edge case in the spec
has a fixture page or a test in T001, T002 or T004. No CRITICAL findings.
Next: design review.

## 2026-09-30T00:40:38Z · S3R design review

Did: rebased onto origin/main after FS-004 merged (f38982b); plan revised for its `BodyRewriter`
and article markup; verify green on 6f86d91. One reviewer, three lenses: approve, 0 critical/high,
5 low (ARCH-001 slice titles by offset; ARCH-002 one emptiness guard; ARCH-003 no neighbour shape
check; SPEC-001 demo edit narrowed to settings.rst; ARCH-004 hidden/orphan cases on the contents
source). All applied and checked against their evidence (D6). Receipts green.
Next: plan notice to the orchestrating session, then US1.

## 2026-09-30T00:58:00Z · Implementer US1 · T001

Did: `mvp_sphinx/headings.py` `PageHeadings` (HTMLParser, `convert_charrefs=False`, titles sliced
by offset as `BodyRewriter` computes positions). New source `tests/sphinx/reading/` (index, long,
single, plain; builds with no warnings) and the `reading_build` session fixture.
Verified: red first (`ModuleNotFoundError: mvp_sphinx.headings`), then
`uv run pytest tests/test_headings.py -q` 16 passed; `uv run pre-commit run --all-files` and
`uv run mypy` passed.
Next: T002, the view, page and components.
Watch: `reading_app` is added in T002.

## 2026-09-30T01:10:00Z · Implementer US1 · T002

Did: `PageView.get_context_data` and `get_headings`; `page.html` wraps the article in the first
column and draws the second column (`<aside>`) inside the one `{% if headings %}` guard;
components `on_this_page.html` (named `nav`, outer list carries `menu menu-sm`) and
`heading_list.html` (recursive); `reading_app` fixture; `TestOnThisPage`; `On this page` msgid
added with `makemessages -l en` (it also refreshed the `page_body.py` line reference and the
creation date). Every layout class was checked in the packaged stylesheet.
Verified: red first (13 of 14 failed: no `nav` on the page; the "plain" test passes before the
change by nature); then `uv run pytest tests/test_views.py::TestOnThisPage -q` 14 passed;
`uv run pytest tests/test_views.py tests/test_headings.py tests/test_demo.py -q` 120 passed;
pre-commit and mypy passed. Probe: forcing the guard true fails the "plain" test.
Next: T003, demo guide section, README, CHANGELOG.
Watch: sticky offset (`top-3`) and the column width are for the walkthrough by eye.

## 2026-09-30T01:25:00Z · Implementer US1 · T003

Did: `demo/docs/settings.rst` gains one section (the single-entry state); README subsection
"The page's own headings" under Usage; CHANGELOG Unreleased, Added, one entry. No page under
`docs/` describes a name this story touched (`docs/ROADMAP.md` is the plan, not current behaviour).
Verified: `uv run pytest tests/test_demo.py -q` 5 passed, unchanged; the demo guide builds with
`sphinx-build -b json -q -W` (exit 0) and the Settings page's `toc` holds one section.
Next: full verify, then the completion report.
Watch: US2 adds its README paragraph beside this subsection.

## 2026-09-30T01:32:00Z · Implementer US1 · T003 (docs gate)

Did: the first `forge verify` run failed its docs step (`PageHeadings` quoted on no page). README
now quotes `PageHeadings.from_toc(toc)` in the subsection T003 added, as it does for `BodyRewriter`.
Verified: full verify re-run, result in the completion report.

## 2026-09-30T10:10:00Z · Implementer US2 · T004

Did: `PageView.get_context_data` (the one) now adds `previous_page` and `next_page` from the new
`get_neighbour(key)`; `page_links.html` component (named `nav`, `rel="prev"` / `rel="next"` cards,
own both-empty guard, layout from classes the packaged stylesheet emits, checked one by one);
`page.html` draws it below the article in the first column, search form untouched; README
paragraph beside "The page's own headings"; CHANGELOG entry; catalogue refreshed with
`makemessages -l en`. `TestPreviousAndNextPage`, 12 tests.
Verified: red first (`uv run pytest tests/test_views.py::TestPreviousAndNextPage`: 9 failed, 3 passed
by nature: one-page build, orphan, general index); then 12 passed. `uv run pre-commit run --all-files`
passed (ruff, mypy, deptry).
Next: T005, the rebuild test.
Watch: the brief and tasks.md say `hidden-page/` has both links, but in the `contents` source it is
the last page in reading order (hidden toctree comes last in `index.rst`), so it has a previous link
only. The test asserts what the source gives: previous is `reference/api/`, and that page's next
link leads to `hidden-page/`, so hidden toctrees feed the links. No source was edited.

## 2026-09-30T10:25:00Z · Implementer US3 · T005

Did: `TestReadingAfterARebuild`, two tests. The fixture copies `tests/sphinx/reading/` into
`tmp_path`, builds it, points the demo app at the build, then edits the front page's source
(a new section) and inserts a page first in its toctree, and rebuilds into the same output
directory with the `sphinx_build` fixture. One test checks the new section's anchor in "On this
page", the other that the next link leads to the inserted page.
Verified: `uv run pytest tests/test_views.py::TestReadingAfterARebuild` 2 passed on the first run,
as tasks.md expected (the view reads the page file on every request), so there was no red step.
Probe: replacing the rebuild call with `pass` fails both tests, so they depend on the rebuild.
Next: full verify, then the completion report.
Watch: no source under `tests/sphinx/reading/` was edited.
