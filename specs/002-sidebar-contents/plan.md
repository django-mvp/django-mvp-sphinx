# Implementation Plan: Show the documentation's contents in the app sidebar

**Branch**: `002-sidebar-contents` | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md) ·
**Research**: [research.md](research.md) · **Tasks**: [tasks.md](tasks.md)

## Summary

A small Sphinx extension, `mvp_sphinx.navigation`, walks every toctree from the root document when
a JSON build finishes and writes the whole contents into the build as `navigation.json`. On the
Django side, each `DocumentationApp` gets a `DocumentationMenu` that reads that file through
`DocsBuild`, turns it into django-mvp menu items (captioned toctrees → `MenuGroup`, a page with
pages of its own → `MenuCollapse` opening on its own page), and rebuilds only when the file changes.
Marking the current page and opening the groups around it is django-flex-menus' own path matching
(research R3). A missing or unreadable file gives a contents holding only the front page. This is
the reviewed prototype (R1) with its Sphinx import, error handling and write atomicity corrected.

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2 / 6.0 / 6.1

**Primary Dependencies**: django-mvp ≥ 0.25.0 (`MenuGroup`, `MenuCollapse`, the sidebar
renderer), django-flex-menus ≥ 0.4.5 (`Menu`, `MenuItem`). Sphinx stays dev-only; the extension
runs inside the host's own Sphinx build (R6).

**Storage**: none. `navigation.json` in the docs build is the only source of the contents.

**Testing**: pytest + pytest-django; real Sphinx builds from sources under `tests/sphinx/`, built
once per session.

**Performance Goals**: one `stat` of the navigation file per request per documentation app; the
file is read and the tree rebuilt only when it changed (R4).

**Constraints**: drawing the contents never imports Sphinx (FR-017); no read failure ever raises
out of the menu (FR-018, R4); the contents is the same tree on every page (FR-009).

**Scale/Scope**: docs of tens to a few hundred pages, several documentation apps per host.

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I Testing | Test-first per task; extension tested against real Sphinx builds, menu through `process()` and through `client`. |
| II Simplicity | One extension module, one menu class, one `DocsBuild` method. No settings, no cache beyond "rebuild when the file changed". |
| III Anti-abstraction | `DocumentationMenu` subclasses flex_menu's `Menu`, the one hook the shell processes; no base class of our own. |
| IV Integration-first | Acceptance tests open pages through `client` and read the sidebar a person sees. |
| V Security | Titles and captions are plain text, auto-escaped (FR-014). The navigation file is read through `contained_file`, inside the build. |
| VI Documentation | README gains the `extensions = ["mvp_sphinx.navigation"]` line in the story that introduces it; CHANGELOG Unreleased entry; AGENTS.md's "not built yet" sentence updated. |
| VII Dependencies | None added. deptry DEP004 ignore for `sphinx`, justified (R6). |
| VIII i18n | The front page and "page itself" entry labels are `gettext_lazy`; catalogue refreshed. |
| IX Data model | No models. |
| X Cohesion | Reading, validating and stamping the file are `DocsBuild` methods beside the page and file lookups; the build-time walk is one `NavigationWriter` class; turning the file into menu items is the menu's. |
| XI Compatibility | New public names only (`mvp_sphinx.navigation`, `DocumentationMenu`); nothing removed. |
| XII Scope | Sphinx only in the extension; serving reads a file. |
| XIII Host look | The contents is the app sidebar's menu, drawn by django-mvp's renderer; no navigation column in the page. |

No violations. Complexity tracking is empty.

## Design

### The navigation file

`navigation.json` at the root of the docs build:

```json
{
  "groups": [
    {"caption": "Getting started", "entries": [
      {"title": "Install", "url": "install/", "children": []},
      {"title": "Guides", "url": "guides/", "children": [
        {"title": "Import", "url": "guides/import/", "children": []}
      ]}
    ]},
    {"caption": "", "entries": []}
  ]
}
```

One group per toctree on the root document, in document order, hidden ones included; `caption`
is `""` for an uncaptioned toctree, whose entries the menu places at the top level. `url` is the JSON builder's address for the page (R2), relative
to the app's prefix. No title for the front page is stored: the front page entry carries a fixed
label (below).

### The extension — `mvp_sphinx/navigation.py`

The module the host names in `conf.py`: `extensions = ["mvp_sphinx.navigation"]`. It imports
`sphinx.addnodes` and `DocsBuild.NAVIGATION_FILE` (from `mvp_sphinx.docs_build`, which imports
neither Django nor Sphinx), and nothing from Django, so the docs build needs no Django settings.

- One class, `NavigationWriter`, constructed with the Sphinx `app` (it reads `env` and `builder`
  from it), holds the walk: the groups of the root document, the entries of one toctree, the
  toctrees of one page, and the write, as methods (Article X). `setup(app)` and the
  `build-finished` handler stay module-level and only construct it. `setup` returns
  `{"version": ..., "parallel_read_safe": True, "parallel_write_safe": True}`.
- On `build-finished`: return when `exception` is set or `app.builder.name != "json"` (only the
  JSON build is served; R2). Otherwise build the groups from the root document's toctrees
  (`app.config.root_doc`) and write the file **atomically**: `Path.write_text` to the fixed
  sibling name `navigation.json.tmp`, so it takes the umask default like every other file in the
  build, then `os.replace` onto `navigation.json` (R1). Never `tempfile.mkstemp` or
  `NamedTemporaryFile`: their 0600 mode would make the file unreadable to a web server running as
  another user, and FR-018 would silently turn that into a front-page-only sidebar (design review
  ARCH-002).
- Entries of a toctree: for each `(title, ref)`, skip it when `ref` is `'self'`, not in
  `env.titles` (external link or missing page), or already on the path from the root down to this
  toctree (a cycle, or a page listing itself) — FR-011, FR-012. Otherwise the entry is
  `{"title": title or env.titles[ref].astext(), "url": builder.get_target_uri(ref), "children":
  ...}` where `children` is the flattened entries of every toctree in `ref`'s own doctree, in
  order, captions ignored below the root (FR-005, FR-007). A page listed twice is visited twice
  (FR-012); the ancestor set, not a global "seen" set, is what stops recursion.
- Function names are plain (no leading underscores). The module docstring is the extension's
  documentation for a reader of the source.

### Reading it — `DocsBuild.navigation()`

`mvp_sphinx/docs_build.py` gains `NAVIGATION_FILE = "navigation.json"` and
`navigation() -> list[dict] | None`: the file's `groups`, or `None` when the file is absent or
cannot be read or decoded (`(OSError, ValueError)`, which covers `JSONDecodeError` and
`UnicodeDecodeError` without a broad `except`), or is not the shape above (groups a list of
objects with a string `caption` and a list `entries`; each entry an object with string `title`,
string `url` and list `children`, recursively). The file is found through `contained_file`, like
every other lookup. The shape check is a recursive `@staticmethod` on `DocsBuild`, so the menu can
trust what it gets. A `navigation_stamp()` method beside it returns the file's
`(st_mtime_ns, st_size, st_ino)` or `None`, for the menu's stamp. The file is in the same trust
domain as the `.fjson` pages the view already renders, so entry addresses are not filtered
(design review SEC-001); FR-010 holds because the menu prefixes every address with the app's own
front page address.

### The menu — `mvp_sphinx/menus.py`

`DocumentationMenu(Menu)`, constructed by `DocumentationApp.__init__` as
`DocumentationMenu(f"mvp_sphinx-{namespace}", app=self)` in place of FS-001's empty `Menu`
(same name, so nothing else changes).

- One `threading.Lock` per menu instance, held across `refresh()` **and** the
  `super().process(...)` call in `process(request, **kwargs)`, so a rebuild's swap of `children`
  and another request's snapshot of it cannot interleave (research R5; design review ARCH-001).
  The menu's `extra_context` carries `{"label": app.name}`, so the sidebar's list has a name.
- `refresh()`: the stamp is `(build_dir as given, the app's front page address, the navigation
  file's `DocsBuild.navigation_stamp()`)`. The build directory is part of the stamp because
  a host (and the suite) may repoint `build_dir`; the front page address because the mount prefix
  can differ per URLconf. Same stamp → return. Otherwise read `DocsBuild(app.build_dir).navigation()`,
  build the new children list completely, then assign `self.children` and store the stamp, all
  under the lock (R5). `stat` failing is a `None` part of the stamp, never an exception.
- Children: first a `MenuItem` for the front page, label `_("Overview")` (the prototype's entry,
  which the owner approved), `url` the front page address. Then per group: a captioned group is
  a `MenuGroup` labelled with the caption holding its entries; an uncaptioned one contributes its
  entries at the top level in its place (FR-002–FR-004). An entry with no children is a `MenuItem`
  with `url = front page address + entry url`; one with children is a `MenuCollapse` labelled with
  the title whose first child is a `MenuItem` for the page itself, label `_("Overview")`, followed by
  its children's items (FR-005). No icons (prototype). Labels go in `extra_context["label"]`, never
  a `label=` keyword; items are built bottom-up and passed as `children=`, so none sits on
  flex_menu's global root on its own.
- Item names are made from the group and entry positions (`"g0-2-1"`-style), unique within the
  menu; flex_menu requires unique names among siblings.
- Labels are the plain strings from the file; nothing is marked safe (FR-014).
- A `None` from `navigation()` gives the front page entry alone (FR-018).

Marking current and opening groups is flex_menu's `match_url` against `request.path` plus parent
propagation (R3). Consequences, recorded as decisions: a page listed twice is marked at both places
(FR-013 marks "the page being read"; the spec's edge case keeps both entries); a page no toctree
lists matches nothing (FR-013); the front page entry is marked only on the front page.

### Two apps, other prefixes

Each `DocumentationApp` owns its menu, its build and its front page address, so FR-010 and FR-019
need no code beyond the stamp including the prefix. Covered by tests with the handbook app mounted
at `manuals/admin/`.

### Tests and fixtures

- `tests/sphinx/contents/` — a new source, built with the extension: two captioned toctrees, an
  uncaptioned toctree between them, a hidden toctree, a page with sub-pages three levels deep, an
  entry with an explicit title, a title containing `<b>`-style characters, a page listed by two
  toctrees, an external link, a `self` entry, a toctree pointing back up the tree, and an
  `:orphan:` page no toctree lists. It deliberately provokes Sphinx warnings (R2), so
  `sphinx_json_build` gains a way to build without the no-warnings assertion for this source only.
- `tests/sphinx/guide/conf.py` and `tests/sphinx/handbook/conf.py` gain the extension, so the
  demo-style app and the second app both carry contents (the no-warnings assertion stays for them).
- A test-only way to mount the contents build: point the demo app (`docs_app`-style fixture) or the
  handbook at it; no new mount.
- Modules mirror the source: `tests/test_navigation.py` (extension, through real builds),
  `tests/test_docs_build.py` (`TestNavigation`), `tests/test_menus.py` (`DocumentationMenu` through
  `process()` with request-factory requests), `tests/test_views.py` / `tests/test_mounted.py` for
  what a reader sees through `client`.
- No test asserts label wording, CSS classes, or layout (testing standard). Marking is asserted on
  the processed tree's `selected`, which is the contract this package supplies; the shell draws it
  (design review SPEC-001). Rendered-page tests find sidebar links by role and address.

### Demo

`demo/docs/conf.py` gains the extension; `demo/docs/index.rst` gains two captioned toctrees and the
tutorials page keeps its nested page, so the walkthrough reaches every state: captioned groups, a
top-level page, a page with pages of its own, the front page entry. The build stays gitignored;
AGENTS.md's build command is unchanged.

## Story order

US1 → US2 → US3, sequential, in the feature worktree. All three touch `mvp_sphinx/menus.py` and its
tests, so they cannot run in parallel.

## Project Structure

```text
mvp_sphinx/
├── docs_build.py          # + NAVIGATION_FILE, navigation(), navigation_stamp()
├── menus.py               # new: DocumentationMenu
├── mounted.py             # menu = DocumentationMenu(...)
├── navigation.py          # new: the Sphinx extension
└── locale/en/LC_MESSAGES/django.po
demo/docs/                 # conf.py extension, captioned toctrees
tests/
├── sphinx/contents/       # new edge-case source
├── sphinx/guide/conf.py, sphinx/handbook/conf.py
├── conftest.py
├── test_navigation.py, test_menus.py  # new
└── test_docs_build.py, test_views.py, test_mounted.py
```

**Structure Decision**: single Django app package, as FS-001 left it.

## Complexity Tracking

None.
