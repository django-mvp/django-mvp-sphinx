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
