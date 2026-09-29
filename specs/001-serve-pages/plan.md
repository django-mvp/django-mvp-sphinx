# Implementation Plan: Serve Sphinx documentation pages inside the application shell

**Branch**: `001-serve-pages` | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md) ·
**Research**: [research.md](research.md) · **Tasks**: [tasks.md](tasks.md)

## Summary

A `DocumentationApp` on django-mvp's `MountedApp` serves one `sphinx-build -b json` build under the
prefix a host mounts it at. One view answers every address under the prefix: it serves a file from
the build's `_images`/`_downloads` folders, renders a page's `.fjson` through the host's
`base.html` inside the application shell, redirects a slashless page address, and answers
anything else with the host's ordinary 404. Everything is read from disk per request, and nothing
imports Sphinx. The build is reached through one small class, `DocsBuild`, which owns the lookups
and their containment checks. The design follows the reviewed prototype (research R2) minus its
django-sphinx-view dependency and minus the contents menu, which is #5.

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2 / 6.0 / 6.1

**Primary Dependencies**: django-mvp ≥ 0.24 (`MountedApp`, `mount`, `PageMixin`, the shell's
`base.html`), django-flex-menus (the app's own empty `Menu`), django-cotton. No new runtime
dependency. Sphinx joins the `dev` group only, to build docs for the tests and the demo (R6).

**Storage**: none. The docs build on disk is the only input.

**Testing**: pytest + pytest-django; real Sphinx builds made once per session into
`tmp_path_factory` directories from sources under `tests/sphinx/`.

**Target Platform**: any host project on django-mvp.

**Project Type**: reusable Django app (library).

**Performance Goals**: one JSON read per page request; no caching (FR-012 forbids stale reads, and
a page file is small).

**Constraints**: serving never imports Sphinx (FR-013); nothing but images and downloads is ever
returned as a file (FR-008); a missing build never breaks start-up (FR-011).

**Scale/Scope**: one build per documentation app, several apps per host.

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I Testing | Every task is test-first against the spec's scenarios; tests mirror `mvp_sphinx/` modules; real Sphinx output, no mocks. |
| II Simplicity | One view, one build class, one template, one mounted-app class. No caching, no settings. Sphinx added to `dev` only, justified in R6. |
| III Anti-abstraction | No base classes of our own. `DocsBuild` exists because two call sites (pages, files) share its root and containment rule, and #5/#7 read the same build. |
| IV Integration-first | Acceptance tests go through `client` against a mounted app, exactly as a host touches it. |
| V Security | Containment for every lookup (R5), NUL-byte and traversal tests, no build file other than images/downloads returned. Body rendered `|safe` by stated trust decision D11; titles stripped to text and auto-escaped. |
| VI Documentation | README gains a usage section and CHANGELOG an Unreleased entry, each story extending it for the names it introduces. |
| VII Dependencies | No runtime dependency added. `deptry` stays green. |
| VIII i18n | The default name and every template string are translatable; `mvp_sphinx/locale/en` catalogue added. |
| IX Data model | No models. |
| X Cohesion | Build lookups are methods of `DocsBuild`; page title and breadcrumbs are view methods; mounting is the `DocumentationApp` class. |
| XI Compatibility | First public API; nothing to deprecate. |
| XII Scope | No Sphinx at serve time, one build per app, several apps by mounting several. |
| XIII Host look | Extends the host's `base.html`, shell components only, no Sphinx theme, no colours of its own. |

No violations. Complexity tracking is empty.

## Design

### Public API

```python
# host project: urls.py
from pathlib import Path
from mvp.mounted import mount
from mvp_sphinx.mounted import DocumentationApp

docs = DocumentationApp(build_dir=BASE_DIR / "docs" / "_build" / "json")
urlpatterns = [mount("docs/", docs)]

# host project: menus.py
AppMenu.append(docs.menu_item())

# a second build
handbook = DocumentationApp(
    build_dir=BASE_DIR / "handbook" / "_build" / "json",
    name=_("Administrator's handbook"),
    namespace="handbook",
)
```

`DocumentationApp(MountedApp)` in `mvp_sphinx/mounted.py`:

- Class attributes, all settable by keyword: `name = _("Documentation")`, `icon = "document"`
  (registered in django-mvp's icon pack), `namespace = "docs"`, `build_dir = None`,
  `view_class = PageView`.
- `__init__` raises `ImproperlyConfigured` when `build_dir` is not given; builds `urls` as
  `([path("", view, name="index"), path("<path:path>", view, name="page")], namespace)` with
  `view = view_class.as_view(app=self)`; sets `landing = f"{namespace}:index"`; sets `menu` to an
  empty `flex_menu.Menu` named from the namespace (R3: the shell processes every app's menu on
  unclaimed host pages, and a Menu's name is global). #5 replaces that menu with the contents.
- The build directory is never touched at construction, so a missing build cannot fail start-up.

`DocsBuild` in `mvp_sphinx/docs_build.py`, constructed per request from `app.build_dir`:

- `page(path) -> dict | None`: `""` → `index.fjson`; `"a/b/"` → `a/b/index.fjson`, then
  `a/b.fjson` (a folder's index first, as the prototype). Any other path (no trailing slash) →
  `None`. The candidate must resolve inside the build root and be a file. A file that exists but
  is not valid JSON raises — a broken build is a server error (D9).
- `file(path) -> Path | None`: only when the first segment is `_images` or `_downloads`; the
  target must resolve inside that folder (not merely the build) and be a file. `ValueError` /
  `OSError` from the filesystem → `None`.

`PageView(PageMixin, TemplateView)` in `mvp_sphinx/views.py`, `template_name =
"mvp_sphinx/page.html"`, `app = None` (set by `as_view`):

1. `file = build.file(path)` → `FileResponse` with the guessed content type (FR-007). Never
   redirected (FR-009).
2. `page = build.page(path)` → render.
3. No page, no trailing slash, and `build.page(path + "/")` exists → `HttpResponsePermanentRedirect(
   request.get_full_path(force_append_slash=True))` (FR-009, D8).
4. Otherwise `Http404`, so the host's own 404 handler answers (FR-010, FR-011).

Context: `doc` (the page data, so #3 and #6 can reach `toc`, `prev`, `next` without a view
change) plus PageMixin's `page`. Page title: `unescape(strip_tags(doc["title"]))`, auto-escaped
where drawn. Breadcrumbs: front page → `[{"text": app.name}]`; any other page → app name linking to
`reverse(f"{app.namespace}:index")`, each parent with its relative `link` made absolute against
`request.path`, then the page with no link (FR-005).

Template `mvp_sphinx/templates/mvp_sphinx/page.html`: extends `base.html`; `title` block is
`page.title`; `content` is `c-page` > `c-container` > `<article class="prose …">{{ doc.body|safe
}}</article>`. No `c-page.title`, so the body's own `<h1>` is the page's only one (R4, D4).

### Tests and fixtures

- `tests/sphinx/guide/` — Sphinx source: front page whose title contains inline code, a top-level
  page, `section/index.rst`, `section/nested/page.rst` (parents chain of two), an image, a
  `:download:`, cross-page links. `tests/sphinx/handbook/` — a two-page second source.
- `tests/conftest.py` — session fixtures build each source with
  `sphinx.cmd.build.build_main(["-b", "json", "-q", src, out])` into `tmp_path_factory`; function
  fixtures point the mounted apps at those builds by setting `build_dir` on the app instances
  (monkeypatch), which the view reads per request.
- `tests/urls.py` — keeps the demo's routes (the demo mounts its own guide at `docs/`) and mounts
  the handbook at a two-segment prefix `manuals/admin/` with `namespace="handbook"`.
- Modules mirror the source: `tests/test_docs_build.py`, `tests/test_views.py`,
  `tests/test_mounted.py`; demo wiring in `tests/test_demo.py`.

### Demo

`demo/docs/` holds a small user guide (front page, a nested page, an image, a download) and
`demo/mounted.py` the demo's `DocumentationApp` pointed at `demo/docs/_build/json` (gitignored),
mounted at `docs/` and added to the demo sidebar. AGENTS.md gains the one command that builds it.
This is the page the walkthrough shows; the full demo user guide is #8.

## Story order

US1 → US2 → US3 → US4, sequential, in the feature checkout. US2–US4 each extend the view US1
creates, so they cannot run in parallel without editing the same file.

## Project Structure

```text
mvp_sphinx/
├── docs_build.py          # DocsBuild: page and file lookups, containment
├── mounted.py             # DocumentationApp
├── views.py               # PageView
├── locale/en/LC_MESSAGES/django.po
└── templates/mvp_sphinx/page.html
demo/
├── docs/                  # demo guide source (build is gitignored)
├── mounted.py
├── menus.py, urls.py      # mount + menu entry
tests/
├── sphinx/guide/, sphinx/handbook/
├── conftest.py, urls.py
├── test_docs_build.py, test_views.py, test_mounted.py, test_demo.py
```

**Structure Decision**: a single Django app package, the layout the scaffold already has.

## Complexity Tracking

None.
