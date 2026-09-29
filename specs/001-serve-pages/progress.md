# Progress — 001 Serve Sphinx documentation pages inside the application shell

## 2026-09-29T22:57:18Z · S3 plan

Did: no feature delivered since this spec landed, so no spec-against-spec re-read. Planned from
the reviewed prototype (django-mvp `wip/sphinx-docs-in-sidebar`) without django-sphinx-view:
research.md (Sphinx JSON output probed on 9.1.0), plan.md, tasks.md — 4 stories, 9 tasks.
Decisions D13–D17 appended.
Next: design review.
Analyze: every FR-001–FR-017 and SC-001–SC-005 maps to at least one task; spec edge cases (markup
titles, slash pairs, multi-segment prefix, broken page file) each have a test in T004/T008/T009.
No CRITICAL findings.

## 2026-09-29T23:05:21Z · S3R design review

Did: one reviewer, three lenses; approve, 3 medium + 5 low, all applied as plan/tasks edits (D18).
Next: plan notice, then US1.

## 2026-09-29T23:08:30Z · Implementer US1 · T001

Did: added Sphinx (9.1.0) to the dev group; guide source (front page and section index titled with inline code, top-level page, section/nested/page, one PNG, one :download: file, links between pages) and a two-page handbook under tests/sphinx/; session fixtures `guide_build` and `handbook_build` build each once into tmp_path_factory with build_main -b json -q, and fail the fixture if Sphinx returns non-zero or writes to its warnings file.
Verified: a throwaway probe test (deleted, not committed) requested both fixtures and found index.fjson in each, the image under _images and the download under _downloads; `uv run pre-commit run --all-files` passes. No test of the fixture itself, by the task's design, so there is no red step for T001; T002-T005 fail if it drifts.
Next: T002, DocsBuild.page.
Watch: tests/sphinx/ has no __init__.py, so it stays a namespace package and `import sphinx` still resolves to the installed one.

## 2026-09-29T23:09:24Z · Implementer US1 · T002

Did: mvp_sphinx/docs_build.py with DocsBuild(root).page(path): front page, folder index then page file, slashless addresses refused, every candidate resolve()d and checked against the resolved root, filesystem errors (NUL byte) answer None, invalid JSON raises. tests/test_docs_build.py::TestPage (15 cases) against the real guide build.
Verified: red first (module missing), then `uv run pytest tests/test_docs_build.py -x`: 15 passed. Mutation probes: removing the is_relative_to check fails the 3 outside-the-build cases; dropping the root resolve() fails the symlink case.
Next: T003, DocumentationApp and PageView.
Watch: the containment helper is private (_contained_file); US2's file() will need the same check against _images/_downloads.

## 2026-09-29T23:11:29Z · Implementer US1 · T003

Did: DocumentationApp (MountedApp subclass; namespace derives urls, landing and an empty flex_menu Menu; build_dir required but never touched at construction), PageView (PageMixin + TemplateView, reads app.build_dir per request through DocsBuild, Http404 for no page) and mvp_sphinx/page.html (extends base.html, article.prose holding body|safe, no c-page.title). pyproject: django-mvp>=0.25.0, django-flex-menus>=0.4.5, DEP002 ignore removed, uv lock. Demo instance in demo/mounted.py mounted at docs/ in demo/urls.py; `docs_app` fixture points it at guide_build.
Verified: 34 passed across the touched test files plus the existing demo/smoke tests; mypy and pre-commit clean. Mutation probes: dropping the template's extends fails the shell-landmark test; dropping |safe fails four tests.
Next: T004, tab title and breadcrumbs.
Watch: on a docs page the sidebar draws the app's empty menu, so the shell's 'Main navigation' nav is absent; the landmark test asserts the shell's <aside> and <main> instead. The h1 test names each page's title text from the fixture rather than reading page.title, so T004 owns the title's first red.
Attempts: 2 on T003 (one setup TypeError, fixed with PageView.app = None; one test that asserted a nav the docs sidebar does not draw).

## 2026-09-29T23:12:21Z · Implementer US1 · T004

Did: PageView.get_page_title (title HTML stripped to text and unescaped) and get_breadcrumbs (front page: app name alone; otherwise app name linking to <namespace>:front_page, each parent's relative link joined to request.path, then the page unlinked). Titles are auto-escaped where the shell draws them.
Verified: red first (3 failed; the app-name-in-tab test already passed because the shell adds the mounted app's name), then `uv run pytest tests/test_views.py tests/test_mounted.py -q`: 15 passed. Mutation probes: returning the title unstripped fails the tab and breadcrumb tests; using the parent link unjoined fails the breadcrumb test.
Next: T005, rebuilds and no-Sphinx tests.
Watch: none.

## 2026-09-29T23:13:18Z · Implementer US1 · T005

Did: TestServingWithoutSphinx in tests/test_views.py: a page file rewritten in a copy of the build between two requests shows the change on the second (FR-012); with sys.modules['sphinx'] and every imported sphinx.* set to None by monkeypatch, the front page and a nested page still answer 200 with their content (FR-013).
Verified: `uv run pytest tests/test_views.py -q`: 15 passed. These tests passed on first run because T003's view already reads per request and never imports Sphinx, so there was no red step; instead I mutated the mechanism: a lazy `import sphinx` inside PageView.get fails both no-Sphinx cases, and a cached page read fails the rebuild case.
Next: T006, documentation, translations, demo guide.
Watch: a module-level `import sphinx` in mvp_sphinx/ is not caught by the sys.modules test (the module is imported before the patch); deptry is what catches that, as the plan says. Also corrected the criteria lists on T003 (SC-001, SC-002) and T004 (none) in feature-state.json.

## 2026-09-29T23:14:37Z · Implementer US1 · T006

Did: README Usage section (sphinx-build -b json, DocumentationApp, build_dir, mount, menu_item, Sphinx not needed where the site runs); CHANGELOG Unreleased entry; demo guide source in demo/docs/ (front page, getting-started with an image and a download, tutorials/index and tutorials/first-page), demo/docs/_build/ gitignored, AGENTS.md demo section gains the build command (and its 'none of it is built yet' sentence now says page serving is); docs.menu_item() in demo/menus.py; mvp_sphinx/locale/en/LC_MESSAGES/django.po from makemessages; TestDocumentationEntry in tests/test_demo.py.
Verified: red first (the sidebar had no /docs/ link), then green; the demo guide builds with an empty warnings file; pre-commit clean.
Next: full verify, then the completion report.
Watch: the .po header is makemessages' default (placeholders); the CHANGELOG still carries the scaffold line 'not yet doing anything'.

## Addendum · Implementer US1 · T006

Did: the docs step of the verify run named `DocsBuild` and `PageView` as public names no page quotes as code, so the README's Usage section now quotes both and the `view_class` hook.
Verified: re-ran the full verify after this change (result in the completion report).

## 2026-09-29T23:19:02Z · Implementer US2 · T007

Did: DocsBuild.file (only `_images/` and `_downloads/`; the target must resolve inside its own folder, resolved first; `_contained_file` gained an optional `within` folder) and PageView.get step 1: a file answers with a FileResponse and the guessed content type. README says images and downloads are served and nothing else; CHANGELOG entry.
Verified: red first (`uv run pytest tests/test_docs_build.py -k TestFile`: 18 failed, AttributeError on `file`), then `uv run pytest tests/test_views.py tests/test_docs_build.py -q`: 66 passed; `uv run pytest tests -q`: 78 passed; pre-commit clean (mypy needed a `type: ignore[override]` because a file answers with a streaming response). Mutation probes: dropping the `_images`/`_downloads` check fails 17 tests; comparing against the build root instead of the folder fails 7.
Next: T008, redirects, not found, missing build, broken page.
Watch: the guide's image and download are on `page/`, not the front page (the brief says front page); the tests read them from `page/`. The traversal client tests reach the view with the `..` intact (checked: resolver kwargs `path='_images/../environment.pickle'`), so the 404 is DocsBuild's containment, not URL normalisation.

## 2026-09-29T23:20:09Z · Implementer US3 · T008

Did: PageView.get step 3 (a slashless address with no page but a page at its slashed form answers a permanent redirect to `request.get_full_path(force_append_slash=True)`), step 4 stays Http404. Tests: TestAddresses (301 with query, `/docs?x=1` redirect from CommonMiddleware, slashless unknown 404, image never redirected, unknown address renders the same templates as a non-documentation unknown address, incl. 404.html), TestMissingBuild (overview 200; prefix, page and image 404; a build copied in afterwards is served by the next request), TestBrokenPage (raises JSONDecodeError; 500 with raise_request_exception off). README: missing-build behaviour, slash redirects and CommonMiddleware/APPEND_SLASH, broken build.
Verified: red first (`uv run pytest tests/test_views.py -k "TestAddresses or TestMissingBuild or TestBrokenPage"`: 1 failed, 11 passed; the other tests describe behaviour T002/T003/T007 already delivered), then `uv run pytest tests/test_views.py -q`: 45 passed; pre-commit clean. Mutation probes: catching ValueError around page() fails the broken-page raise test; redirecting without checking that the slashed page exists fails 16 tests.
Next: T009, menu entry, naming, two apps.
Watch: no code was needed for the bare-prefix redirect or the missing build; the tests lock them.

## 2026-09-29T23:21:20Z · Implementer US4 · T009

Did: tests/urls.py mounts a second DocumentationApp (`handbook`, name "Administrator's handbook", namespace `handbook`, build_dir a placeholder until a test points it at handbook_build) at `manuals/admin/`. Tests: TestMenuEntry (entry's view resolves to the front page, following it answers it; a second app's entry leads to its own prefix), TestNamingAnApp (tab and first breadcrumb, front page and nested, carry the host's name and not "Documentation"), TestTwoAppsSideBySide (each build served only at its own prefix; breadcrumb hrefs stay within each prefix; each tab names only its own app). README: naming an app, several apps; CHANGELOG entry. No code change in mvp_sphinx/.
Verified: `uv run pytest tests/test_views.py tests/test_mounted.py -q`: 57 passed; pre-commit clean. These tests passed on first run because T003/T004 already read name and namespace from the app per request, so there was no red step; mutation probes instead: hard-coding the `docs:front_page` reverse fails the side-by-side breadcrumb test, hard-coding "Documentation" as the front-page crumb fails a test only after I added the named front-page breadcrumb test.
Next: full verify, then reports.
Watch: the fixture that points `handbook` at its build lives in tests/test_views.py and is repeated inline in test_mounted.py, because conftest.py is outside this task's file list.

## 2026-09-29T23:24:25Z · S5 converge

Did: all four stories done; one cleanup commit (file lookups also confined to the build when a file folder is a link; one handbook fixture; changelog). No migrations. ADR 0001 graduated from D2/D3/D16; every decision verdicted. Roadmap R1 marked delivered and rewritten to its delivered form.
Next: review.

## 2026-09-29T23:31:45Z · S6 review

Did: one reviewer, correctness/spec/docs and security lenses; request_changes with 1 high, 1 medium, 1 low. All three fixed test first in one cycle (D21) and each remedy checked against the reviewer's reproduction on the running server.
Next: walkthrough and ready for review.

## 2026-09-29T23:35:45Z · S7 walkthrough round 2

Did: walkthrough passed; the one request (no leading-underscore names) done: contained_file, is_canonical, no _encoding local (D22). Full verify green.
Next: checks green, then merge by the orchestrator.
