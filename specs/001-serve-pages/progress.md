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
