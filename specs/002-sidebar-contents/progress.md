# Progress — 002 Show the documentation's contents in the app sidebar

## 2026-09-29T23:44:00Z · S3 plan

Did: queue row for FS-002 read `in-flight` because the orchestrating session claimed it for this
run; `delivered_since` is empty, so no spec-against-spec re-read. Planned from the reviewed prototype
(django-mvp `wip/sphinx-docs-in-sidebar`, 6da698a) without django-sphinx-view: research.md (premises
read from Sphinx 9.1.0, serializinghtml 2.0.0, django-mvp 0.25.0, flex-menus 0.4.6 as installed),
plan.md, tasks.md: 3 stories, 7 tasks. Decisions D1–D7 appended.
Analyze: FR-001–FR-020 and SC-001–SC-005 each map to at least one task; every edge case in the spec
has a fixture entry in `tests/sphinx/contents/` or a test in T006/T007. No CRITICAL findings.
Next: design review.

## 2026-09-29T23:58:00Z · S3R design review

Did: one reviewer, three lenses; request_changes, 2 high (ARCH-001 non-atomic children swap →
per-menu lock; SPEC-001 planned `menu-active` class assertion → removed), 2 medium (ARCH-002 temp
file mode → fixed sibling name + write_text; ARCH-003 loose functions → NavigationWriter class and
DocsBuild staticmethod), 4 low (SEC-001 url filter removed; SPEC-002 atomic-write test removed;
SPEC-003 `sections` → `groups`; ARCH-004 catch ValueError, invalid UTF-8 case). All applied as
plan/research/tasks/decisions edits and checked against each finding's evidence (D8).
Next: plan notice, then US1.

## 2026-09-29T23:57:00Z · Implementer US1 · T001

Did: `mvp_sphinx/navigation.py` (`NavigationWriter`, `write_navigation`, `setup`), `DocsBuild.NAVIGATION_FILE`, the deptry DEP004 ignore for `sphinx`, the `tests/sphinx/contents/` source, the `sphinx_build` and `contents_build` fixtures, `tests/test_navigation.py`. Sphinx 9.1 stops with a recursion error on any toctree cycle, so the back-pointing toctree is not in the fixture and the fixture builds without warnings: the planned `sphinx_json_build` keyword to allow warnings is not added (D9). The ancestor guard is tested on a stand-in environment.
Verified: `uv run pytest tests/test_navigation.py tests/test_docs_build.py -q` → 53 passed; red first (extension module missing); mutating the ancestor guard, the builder-name check and the title lookup each fails a test; `uv run pre-commit run --all-files` → all hooks pass.
Next: T002, `DocsBuild.navigation()` and `navigation_stamp()`.
Watch: `ref == "self"` needed no clause of its own, since `self` is never in `env.titles`.

## 2026-09-29T23:59:00Z · Implementer US1 · T002

Did: `DocsBuild.navigation()`, `navigation_stamp()` and the recursive `valid_entries` staticmethod; `TestNavigation` and `TestNavigationStamp` in `tests/test_docs_build.py`.
Verified: `uv run pytest tests/test_docs_build.py -q` → 57 passed; red first (`navigation` did not exist); mutating the `ValueError` catch, the url check, the top-level dict check and the inode part of the stamp each fails a test (the inode one after the replacement test was made to hold size and mtime equal); `uv run pre-commit run --all-files` → all hooks pass.
Next: T003, `DocumentationMenu` and the sidebar tests.
Watch: `navigation()` finds the file through `contained_file`, so a symlink pointing out of the build reads as absent (tested).

## 2026-09-30T00:01:00Z · Implementer US1 · T003

Did: `mvp_sphinx/menus.py` (`DocumentationMenu`: `process`, `refresh`, `entry_item`), `DocumentationApp` builds it in place of the empty `Menu`; the guide and handbook sources load the extension; `contents_app` fixture; `TestDocumentationMenu`, `TestServingSideImports` (tests/test_menus.py) and `TestContentsInTheSidebar` (tests/test_views.py). US1 rebuilds the items on every `process()`, with no stamp and no lock (US3).
Verified: `uv run pytest tests/test_menus.py tests/test_mounted.py tests/test_views.py tests/test_navigation.py tests/test_docs_build.py -q` → 149 passed; red first (menu had no label; the handbook test failed until the source loaded the extension); mutations of the address prefix, the label safety, the group class, the uncaptioned entries and the children assignment each fail tests, and adding `import sphinx` to `docs_build.py` fails the subprocess test; `uv run pre-commit run --all-files` → all hooks pass.
Next: T004, README, CHANGELOG, AGENTS.md, demo guide, catalogue, `test_demo`.
Watch: the sidebar tests find the contents list by its `aria-label`, which is the app's name; `TestServingSideImports` uses a subprocess because `sys.modules` blocking cannot show that modules already loaded do not import Sphinx.

## 2026-09-30T00:02:00Z · Implementer US1 · T004

Did: README section "The contents in the sidebar" (the one `conf.py` line, what the sidebar holds, Sphinx still not needed at runtime, what happens without the line); CHANGELOG Unreleased entry; AGENTS.md sentence replaced; demo guide loads the extension and `index.rst` has two captioned toctrees and an uncaptioned one, with three short pages added and the tutorials page and its nested page kept; catalogue refreshed with `django-admin makemessages -l en` (adds "Overview"); `TestDemoGuide` in `tests/test_demo.py`. README text written to the humanizer skill's rules. No page under `docs/` describes a name this story touched (ROADMAP R2 is the plan, not current behaviour).
Verified: `uv run pytest tests/test_demo.py tests/test_menus.py tests/test_mounted.py -q` → 21 passed; the test failed before `conf.py` loaded the extension; `uv run sphinx-build -E -b json -q -w /tmp/demo.warn demo/docs /tmp/demo-out` → exit 0, empty warnings file; `uv run pre-commit run --all-files` → all hooks pass.
Next: full verify, then the completion report. The first full verify failed its docs step on `NavigationWriter`, `setup` and `write_navigation`; the README now quotes them.
Watch: the README's rebuild-on-next-request sentence belongs to US3 (T007) and is not written here.

## 2026-09-30T00:20:00Z · Implementer US2 · T005

Did: `TestCurrentPage` in `tests/test_menus.py`, eight tests on the processed tree of the contents build: a page nested in two groups (only selected link; the three enclosing groups selected), a page with pages of its own (its "page itself" link is the selected link, its group selected), the front page, a page listed twice (both places selected), a top-level page, the `:orphan:` page (nothing selected, tree equal to the front page's), and a request with a query string. No production code changed and no rendered-HTML test was added: the shell draws the marking with a CSS class only, which the brief rules out asserting.
Verified: `uv run pytest tests/test_menus.py::TestCurrentPage -q` → 8 passed on first run, as the task expects (flex_menu's matching does the work). Probed instead of trusting green: pointing the "page itself" link at the wrong address fails 2 tests, moving the front page entry fails 1, and appending to every entry address fails 6; `menus.py` restored after each. `uv run pre-commit run --all-files` → all hooks pass.
Next: full verify, then the completion report.
Watch: no test in `tests/test_views.py` was needed; nothing observable there beyond the CSS class.

## 2026-09-30T00:40:00Z · Implementer US3 · T006

Did: `DocumentationMenu` now keeps a `threading.Lock` per instance, held across `refresh()` and `super().process(...)`, and a `stamp` of `(build_dir as given, front page address, DocsBuild.navigation_stamp())`; `refresh()` returns at once on the same stamp and otherwise builds the whole list and assigns `children` and the stamp together. `TestRefresh` (tests/test_menus.py: page added, page removed, file not read again while unchanged, replaced file read again, another build, same build by another path, another mount prefix) and `TestRebuiltContents` (tests/test_views.py: the same two rebuilds through `client`, one app instance).
Verified: `uv run pytest tests/test_menus.py tests/test_views.py -q` → 90 passed; red first (the read-count test saw two reads, not one); the rebuild tests pass on the old code by design, so probed instead: dropping the build directory from the stamp fails 1 test, dropping the front page address fails 1, replacing the file stamp with `None` fails 3 in test_menus and both `TestRebuiltContents` tests; `menus.py` restored after each. `uv run pre-commit run --all-files` → all hooks pass. The lock has no test, as the plan says.
Next: T007.
Watch: the same-build-by-another-path test uses a symlink, since a copy of the build has a different inode and would rebuild through the file stamp alone.

## 2026-09-30T00:50:00Z · Implementer US3 · T007

Did: `TestContentsUnavailable` in tests/test_views.py through `client`: no navigation file, five unusable files (invalid JSON, a list, `groups` not a list, a non-string caption, an entry with no url) each serve the page with only the front page entry; an unreadable file (`chmod 000`, skipped as root) does too; the overview page answers 200 and still draws the host's own menu and the docs entry with a missing build and with an unreadable file; a file broken mid-run gives the front page only and the full contents again once fixed. README: one sentence that a rebuilt docs build shows on the next request with no restart. No change to `menus.py` was needed: the tests passed on first run, as the task allows.
Verified: `uv run pytest tests/test_views.py tests/test_menus.py -q` → 100 passed; probed: catching only `ValueError` in `DocsBuild.navigation()` fails the two unreadable-file tests, and dropping the `or []` in `refresh()` fails all 10; both restored. `uv run pre-commit run --all-files` → all hooks pass.
Next: full verify, then the completion report.
Watch: the unreadable-file tests skip when the suite runs as root; they ran here as a normal user.
