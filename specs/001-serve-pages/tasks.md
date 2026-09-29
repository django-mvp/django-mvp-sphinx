# Tasks — 001 Serve Sphinx documentation pages inside the application shell

**Branch**: `001-serve-pages` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. Documentation for a public name lands in the task
that introduces it. No test asserts wording, classes or layout (testing standard §1); headings are
found by element, pages by their fixture content.

## Order

**US1 → US2 → US3 → US4, one at a time, in one working tree** (plan, *Story order*).

---

## US1 — Read a documentation page as a page of the site (P1)

Issue: #19. Delivers FR-001 to FR-006 (pages), FR-012, FR-013, FR-015 (default name), FR-017;
SC-001 (pages and links), SC-002, SC-003 (pages).

### T001 — Real Sphinx builds for the suite

**Files**: `pyproject.toml`, `uv.lock`, `tests/sphinx/guide/**`, `tests/sphinx/handbook/**`,
`tests/conftest.py`

Research R1, R6. `uv add --group dev "sphinx>=8.1"`. Guide source per plan *Tests and fixtures*
(front page title with inline code; top-level page; `section/index.rst`;
`section/nested/page.rst`; one PNG image; one `:download:` file; body links between pages);
handbook source with two pages. Session fixtures `guide_build` and `handbook_build` build each once
into `tmp_path_factory` with `sphinx.cmd.build.build_main` (quiet, warnings not fatal but the
fixture sources must build without warnings). Test: the guide build holds `index.fjson`,
`section/index.fjson`, `section/nested/page.fjson`, one file under `_images/` and one under
`_downloads/` — a guard that the fixture still shapes the build the other tests rely on
(put it in `tests/test_docs_build.py`, class `TestFixtureBuild`).

### T002 — `DocsBuild.page`

**Files**: `mvp_sphinx/docs_build.py`, `tests/test_docs_build.py`

Plan, *DocsBuild*. Tests (class `TestPage`): `""` gives the front page's data; `"section/"`
gives the folder's index page; `"section/nested/page/"` gives the nested page; a slashless
address gives `None`; an unknown address gives `None`; `"../"`-style and absolute-looking
addresses (`"../../etc/"`, `"section/../../"`) give `None` even when a matching `.fjson` exists
just outside the build (create one in `tmp_path`); an address with a NUL byte gives `None`; a
missing build root gives `None`; a `.fjson` holding invalid JSON raises (D9). Docstrings per
`docs/contributing/standards/code-documentation.md`.

### T003 — `DocumentationApp` and `PageView`: pages inside the shell

**Files**: `mvp_sphinx/mounted.py`, `mvp_sphinx/views.py`,
`mvp_sphinx/templates/mvp_sphinx/page.html`, `demo/mounted.py`, `demo/urls.py`,
`tests/test_mounted.py`, `tests/test_views.py`, `tests/conftest.py`

Plan, *Public API* and *PageView* steps 2 and 4 only (files, redirect: later stories). The demo
instance (`demo/mounted.py`, `build_dir` → `demo/docs/_build/json`) is mounted at `docs/`; the
suite points it at `guide_build` through a fixture that sets `build_dir` on the instance.
Tests, `TestDocumentationApp`: constructing without `build_dir` raises `ImproperlyConfigured`;
constructing with a directory that does not exist does not touch the disk and does not raise;
its landing reverses to the mount prefix. Tests, `TestPageView` (through `client`): the prefix
answers 200 with the front page's body inside the shell (the shell's own landmark — e.g. the
sidebar's `<aside>`/`<main>` — and the fixture page's text are both present); `section/` and
`section/nested/page/` answer their pages (US1 scenarios 1–3); every served page has exactly one
`<h1>` and it contains the page's title text (scenario 4); every page link in the front page's body,
resolved against the page's address, answers 200 (scenario 8, SC-001 pages).

### T004 — Tab title and breadcrumbs

**Files**: `mvp_sphinx/views.py`, `tests/test_views.py`

Plan, *Context*. Tests: the `<title>` of the front page contains its title as plain text (the
inline-code title shows no `<code>`/`<span>` and no escaped tag text) and the default app name
(scenario 5, FR-015); the front page's breadcrumbs (`response.context["page"]["breadcrumbs"]`)
are the app name alone, with no link (scenario 6); the nested page's breadcrumbs are app name →
front page URL, `section/` parent → its absolute URL, then the page with no link (scenario 7,
FR-005); a parent title with markup appears as plain text.

### T005 — Rebuilds and an environment without Sphinx

**Files**: `tests/test_views.py`

Tests: change a page's `.fjson` body in a copy of the build between two requests; the second
response shows the change (scenario 9, FR-012). With `monkeypatch.setitem(sys.modules, "sphinx",
None)` (and `sphinx.*` submodules already imported popped the same way), the front page and a
nested page still answer 200 with their content (scenario 10, FR-013, SC-003 pages). A subprocess
test runs `python -c` importing `mvp_sphinx.mounted`, `mvp_sphinx.views` and
`mvp_sphinx.docs_build` with `sys.modules["sphinx"] = None` set first, and exits 0.

### T006 — Documentation, translations and the demo guide

**Files**: `README.md`, `CHANGELOG.md`, `AGENTS.md`, `.gitignore`, `demo/docs/**`, `demo/menus.py`,
`mvp_sphinx/locale/en/LC_MESSAGES/django.po`, `tests/test_demo.py`

README: a *Usage* section quoting `DocumentationApp`, `build_dir`, `mount(...)` and the
`sphinx-build -b json` command, stating Sphinx is not needed where the site runs (FS-005 writes
the full quickstart later; this is the minimum the public name needs). CHANGELOG Unreleased
entry. Demo guide source under `demo/docs/` (front page, one nested page, an image, a download);
`demo/docs/_build/` gitignored; AGENTS.md *Demo project* gains the build command. Demo menu entry
`docs.menu_item()` in `demo/menus.py`. `django-admin makemessages -l en` for the package's strings.
Test (`tests/test_demo.py`): the demo sidebar carries the documentation entry linking to `/docs/`.
Humanize the README text (public markdown).

---

## US2 — Images and downloads load with the page (P2)

Issue: #20. Delivers FR-006 (files), FR-007, FR-008; SC-001 (images), SC-003 (files), SC-004.

### T007 — Serving images and downloads, and nothing else

**Files**: `mvp_sphinx/docs_build.py`, `mvp_sphinx/views.py`, `tests/test_docs_build.py`,
`tests/test_views.py`, `README.md`

Plan, *DocsBuild.file*, *PageView* step 1. Tests, `TestFile`: a path under `_images/` gives the
file; one under `_downloads/<hash>/` gives the file; `_images/../environment.pickle`,
`_images/../../outside.txt`, `_downloads/../index.fjson` give `None`; a symlink inside `_images`
pointing outside it gives `None`; a missing name gives `None`; a NUL byte gives `None`; paths
outside the two folders (`globalcontext.json`, `searchindex.json`, `_sources/index.rst.txt`,
`index.fjson`, `_static/…`) give `None`. Tests through `client`: the image `src` in the front page,
resolved against its address, answers 200 with an `image/png` content type and the file's bytes
(US2 scenario 1); the download link answers the copied file's bytes (scenario 2); a missing image
name answers 404 (scenario 3); traversal addresses answer 404 (scenario 4); requests for
`globalcontext.json`, `index.fjson`, `environment.pickle`, `_sources/index.rst.txt` (with and
without a trailing slash) never return those files' bytes (scenario 5, SC-004). Under the
Sphinx-blocked fixture from T005, the image and download still answer (SC-003). README mentions
that images and downloads the pages link to are served, and nothing else in the build.

---

## US3 — Addresses behave like the rest of the site (P2)

Issue: #21. Delivers FR-009 to FR-011, FR-012 (first build); SC-005.

### T008 — Redirects, not found, a missing build and a broken page

**Files**: `mvp_sphinx/views.py`, `tests/test_views.py`, `README.md`

Plan, *PageView* steps 3–4. Tests: `section/nested/page?x=1` (no slash) answers 301 to
`…/page/?x=1` (scenario 1); a slashless address with no page behind it answers 404, not a redirect;
an unknown address answers 404 rendered with the host's `404.html` — the same template a
non-documentation unknown address gets (scenario 2, FR-010); an image address is never redirected
(scenario 5); with `build_dir` pointing at a directory that does not exist, the demo's overview
page still answers 200 and the prefix, a page address and an image address answer 404
(scenario 3); creating the build at that path afterwards makes the next request answer 200
(scenario 4); a page whose `.fjson` is not valid JSON makes the request raise (a server error, not
404; D9). README: one line on the missing-build behaviour.

---

## US4 — The site leads readers to its documentation (P3)

Issue: #22. Delivers FR-014, FR-015 (custom name), FR-016.

### T009 — Menu entry, naming, and two apps side by side

**Files**: `tests/urls.py`, `tests/test_mounted.py`, `tests/test_views.py`, `README.md`,
`CHANGELOG.md`

Plan, *Public API* (second build). `tests/urls.py` mounts the handbook at `manuals/admin/` with
`name` and `namespace="handbook"`; a fixture points it at `handbook_build`. Tests: `menu_item()`'s
link resolves to the app's front page and following it from the demo overview answers the front
page (scenario 1); with a custom name, the tab and the first breadcrumb carry it and not the
default (scenario 2); a page under each app is served from its own build, and each page's
breadcrumb links and tab stay within its own prefix and name (scenario 3, FR-016); a menu entry
is marked current on the app's own pages only (the app's pages, not the other app's). README:
naming an app, and mounting a second build with its own `namespace`.
