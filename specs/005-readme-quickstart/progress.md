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

## 2026-09-30T10:58:00Z · Implementer US2 · T002

Did: wrote the Public surface section (replacing its template comment) and ended it with the sentence
that anything unlisted is internal; it says there are no settings. Deleted
`mvp_sphinx/templates/cotton/mvp_sphinx/example.html`, `TestStarterComponent` and `EXAMPLE_TAG` in
`tests/test_smoke.py`, the `render` fixture in `tests/conftest.py` with its three now-unused imports (the
declared D12 edit, the only pre-existing test edit), and the overview page's "The starter component"
section. `TestPackagedApp` stays. CHANGELOG Unreleased gets one Added entry, nothing under Removed.
Per-entry check against the source (one script run under `tests.settings` with `django.setup()`, plus reads):
- `mvp_sphinx` installed app: `apps.is_installed("mvp_sphinx")` True.
- `mvp_sphinx.navigation`: module imports; `NavigationWriter`, `write_navigation`, `setup` exist (Sphinx's
  hooks, unlisted); `setup` read in navigation.py.
- `DocumentationApp` imports; options `build_dir`, `name`, `icon`, `namespace`, `view_class`, `check` are
  each a class attribute, and one instance built with all six keywords; `menu_item()` is on `MountedApp`
  (MRO DocumentationApp, MountedApp) and returned a `MenuItem` for `<namespace>:front_page`; `menu` is a
  `DocumentationMenu`.
- URL names: `reverse("docs:front_page")` `/docs/`, `reverse("docs:page", kwargs={"path": "x/"})`
  `/docs/x/`, `reverse("docs:search")` `/docs/search/`.
- `PageView`, `SearchView`, `DocsBuild`, `DocumentationMenu`, `PageHeadings`, `BodyRewriter`, `DocsSearch`,
  `PageText`: all import. `PageHeadings.from_toc` and `BodyRewriter.rewrite` are callable classmethods.
- Templates: `get_template("mvp_sphinx/page.html")` and `"mvp_sphinx/search.html"` load. page.html blocks
  `title`, `styles`, `content` and the `mvp-sphinx-content` class read in the file; search.html blocks
  `title`, `styles`, `content`. Context read in `views.py`: PageView supplies `search_url`, `headings`,
  `previous_page`, `next_page`, plus `page_data` and `body` from `get`; SearchView supplies `query`,
  `results` (None or list, each with `title`, `path`, `anchor`, `passage`, plus `href`) and `search_url`.
- Components: `@prop` lines read in all four templates: `on_this_page` `headings`, `heading_list`
  `headings`, `page_links` `previous` and `next`, `search_form` `action` and `query`.
- Static: `finders.find("mvp_sphinx/content.css")` resolves to the package file.
- Settings: `grep "settings\." mvp_sphinx/*.py` finds none.
Extra public name found: the `menu` attribute of `DocumentationApp` (the FS-002 README already described
it), added to the section and raised in concerns.
Verified: `uv run pytest tests/test_smoke.py tests/test_demo.py tests/test_quickstart.py -q` 17 passed.
Blocked: full verify found `tests/test_views.py::TestSearchResults::test_a_word_only_in_the_hosts_pages_lists_nothing`
red. It asserts the word `starter` appears on the overview page, which only the removed "The starter component"
section carried. Fixing it means editing a pre-existing test beyond the D12 authorisation, so it is left
unedited and T002 is reported blocked. The word `demonstration` (in the overview's first section, absent from
`tests/sphinx/search/`) would keep the test's intent; Forge to triage.
Next: report.
Watch: AGENTS.md (Components) still names `<c-mvp_sphinx.example>` and `example.html`; outside T002's files.

## 2026-09-30T10:27:37Z · Forge · US1 and US2 accepted

Did: receipts green (check-receipts --brief). T002 came back blocked on one FS-007 test whose premise
word lived in the removed starter section; Forge changed the word (D16). Conformance flagged
tests/test_quickstart.py as mirroring no module; Forge moved TestQuickstart into tests/test_mounted.py
(D17). README read against the source: quickstart steps, public surface entries (component @props,
view context, template blocks) match.
Verified: forge verify --base origin/main at e7ec597, all six steps passed. tamper-check flags only
the declared edits (conftest.py render fixture, test_smoke.py starter class, test_views.py one word).
story-done US1 (#26), US2 (#29).
Next: US3 dispatch. Carry: AGENTS.md Components section still names the starter component.

## 2026-09-30T10:45:00Z · Implementer US3 · T003

Did: `TestDemoGuideStates` in `tests/test_demo.py` and the `demo_guide_build` / `demo_guide_app`
fixtures in `tests/conftest.py`. The build is module-scoped, `-W`, into a temporary folder, and
`demo.mounted.docs` is pointed at it with `monkeypatch`. The pages walked come from the processed
menu tree's URLs; each state is asserted by structure (no wording, no titles).
Verified: `uv run pytest tests/test_demo.py::TestDemoGuideStates -q` exit 0, 15 passed. All 15
pass against the guide as it stood before the rewrite, because that guide already held every
state; recorded as passing at red (FS-002 T005 precedent). The rewrite is checked against the same
tests in T004.
Next: T004, the guide rewrite, README demo part, AGENTS.md fixes.
Watch: none.

## 2026-09-30T11:10:00Z · Implementer US3 · T004

Did: `demo/docs` rewritten as a user guide for the demo site. Front page with captioned groups
"Using the site" and "Reference" and one uncaptioned page (About); "Your first visit" with
"Signing in" and "Finding your way" under it; the staff guide page; reference pages for the
accounts (wide table, a table in a list item, JSON and plain-text blocks, a download), sharing links
(long page, nested headings, captioned code with line numbers, a long line), notices (every
admonition kind, version notes, images, a figure), the glossary, and one page with a long title.
`shell.png` kept; `notes.txt` replaced by `accounts.csv` as the download. `demo/staff_guide/index.rst`
reworded where it described the package. README: Contributing gains "The demo" (uv sync, migrate,
seed_demo, the two sphinx-build commands as quickstart step 3, runserver, what to open, the three
accounts, absolute links). AGENTS.md: the Components example now names `<c-mvp_sphinx.page_links>`;
the demo section says what the guide is and that TestDemoGuideStates checks it.
Verified: `uv run sphinx-build -b json -W -q demo/docs /tmp/us3-build` exit 0;
`uv run pytest tests/test_demo.py -q` exit 0, 26 passed; `uv run pre-commit run --all-files` passed.
Probed: removing the `danger` admonition and the `:download:` role each turned a
TestDemoGuideStates test red (test_each_admonition_kind_is_drawn, test_a_download_is_served);
reverted.
Next: full verify, report.
Watch: CHANGELOG is not in T004's files and has no entry for the demo guide.

## 2026-09-30T10:36:43Z · Forge · US3 accepted, S5 converge

Did: US3 receipts green, verify green at da2f2d4, tamper-check clean against 99faf6d, guide pages and
README demo part read; story-done US3 (#32). Converge: every FR/SC maps to a done task (FR-001–007,
014 → T001; FR-008–010 → T002; FR-011–013 → T003/T004), no gaps, no new tasks. No migrations.
craft-simplify pass on the diff: one helper for the admonition classes both demo tests collected.
ADR verdicts: D9–D17, none graduate (check-adrs green). Whole-feature tamper-check: only the declared
edits (D12, DR-003, D16).
Next: S6 review.
