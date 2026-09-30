# Progress — 005 Get a project from install to a working docs page by following the README

## 2026-09-30T10:09:39Z · S3 plan

Did: queue row for FS-005 read `in-flight` with no pull request: the orchestrating session's claim
for this run, treated as ready. `delivered_since` is empty, so the spec-against-spec check is
skipped (D9 records the reading of US2.3 now that #9 and #10 have shipped). Worktree `wt-sphinx-005`
off origin/main f8d30be, identity bound, `uv sync`. Research read from the package on main, django-mvp
0.25.0 and django-flex-menus 0.4.6, and the prototype on django-mvp `wip/sphinx-docs-in-sidebar`.
plan.md, research.md, tasks.md: 3 stories, 4 tasks. Decisions D9–D14 appended.
Next: analyze, then design review.

## 2026-09-30T10:17:25Z · S3R design review

Did: one design reviewer (Opus), three lenses. Verdict approve: 2 medium, 5 low, no critical/high.
DR-001–DR-006 applied to plan.md and tasks.md, DR-007 declined (D15). Analyze re-run on the edited
tasks: prerequisites green. stage-exit S3R green. Plan notice sent to the orchestrator.
Next: US1+US2 dispatch.

## 2026-09-30T10:45:00Z · Implementer US1 · T001

Did: `tests/test_quickstart.py::TestQuickstart` (4 tests) with `tests/sphinx/quickstart/` (conf.py
holding only `project` and the step-2 line, an index with one captioned toctree of two pages) and
`tests/urls_quickstart.py` (step 4's app at `help/guide/` under namespace `quickstart`). The build runs
step 3's arguments through `build_main(["-b", "json", "-W", src, out])` into `docs/_build/json` inside
the copied source, as the README's command does. `AppMenu` entry appended (step 5) and popped in
teardown. Tests: front page 200 with the app's navigation landmark at the chosen prefix (US1.1); the
processed menu tree holds one group with both pages in order and each URL answers 200 (US1.1);
the host page's menu entry `href` is the front page and following it serves `index` (US1.2); a page
added to the source and toctree, rebuilt into the same folder, is 404 before and served and listed in
the app sidebar after (US1.5). US1.4 is `TestServingWithoutSphinx` (FS-001), not repeated.
README restructured: Scope & philosophy, Quickstart (before you start, five steps, what you now have,
changing the docs), Using it (every subsection kept), Public surface (still the template placeholder,
T002), Contributing, License. Template comment in Quickstart removed. All snippets use
`from django.conf import settings` and `settings.BASE_DIR`. Step 5 is labelled `yourapp/menus.py`.
No build command mentioned.
Verified: `uv run pytest tests/test_quickstart.py -q` 4 passed. Red: the behaviour already exists on
main, so the tests pass against it (FS-002 T005 precedent). They were probed by mutation instead:
commenting out the `extensions` line failed the contents-group and rebuild tests; removing the
`AppMenu.append` failed the host-entry test. Sphinx 9.1 warns `misc.copy_overwrite` when a changed
source is rebuilt into the same folder, which `-W` turns into a failed build, so the rebuild step passes
`-D suppress_warnings=misc.copy_overwrite` (first build stays a plain `-W`). Also
`uv run pre-commit run --all-files` green.
README before/after (every heading and fact-bearing paragraph of the README at 1e1ea3e):
- Title, description, Scope & philosophy (4 paragraphs): kept verbatim.
- Installation: pip install and `INSTALLED_APPS` after `mvp` -> Quickstart step 1. "requires django-mvp,
  renders in its layout, reads its colours from its theme, nothing useful on its own" -> Before you start.
- Usage intro, build command, "Sphinx needed only where you run it, never imported, can stay out of
  production requirements" -> Quickstart step 3 (reworded). `mounted.py` snippet -> step 4, now with
  `settings.BASE_DIR`. `urls.py` mount -> step 4. `menus.py` snippet -> step 5 as `yourapp/menus.py`.
  "Each page answers under docs/, drawn by your base.html, tab title, `name`, breadcrumbs" -> What you
  now have.
- The contents in the sidebar: the `conf.py` line -> step 2; every other paragraph and the four bullets
  kept under Using it; opening sentence now points at step 2.
- The page's own headings (incl. `PageHeadings.from_toc`, previous/next links, `-E` note): kept, moved
  ahead of Search.
- Search (all 7 paragraphs): kept verbatim.
- Naming the documentation, Choosing who can read it (all paragraphs and snippets, the mounted apps guide
  link, two-audiences snippets): kept; `BASE_DIR` -> `settings.BASE_DIR` and the import line added to
  snippets that have imports.
- Several documentation apps: kept up to the add-menu-item paragraph. The images/downloads paragraph,
  `build_dir` read on every request/404 paragraph, and slash/404/CommonMiddleware/broken-JSON paragraph
  -> new subsection Addresses and files served, verbatim. The `PageView`/`DocsBuild`/`view_class`
  paragraph -> How pages look and the page template, verbatim.
- How pages look (H2) -> H3 under Using it, all paragraphs, the `BodyRewriter` paragraph, the override
  paragraph and the django snippet kept.
- Quickstart and Public surface template comments: Quickstart's removed (filled); Public surface's
  stays until T002.
- Contributing, License: unchanged.
Next: T002.
Watch: `README` claims are not tested (no test reads it); the reviewer's documentation pass is the check.
