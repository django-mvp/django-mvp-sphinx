# Tasks — 002 Show the documentation's contents in the app sidebar

**Branch**: `002-sidebar-contents` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. Documentation for a public name lands in the task
that introduces it. No test asserts label wording, CSS classes chosen for looks, or layout (testing
standard); entries are identified by their address and by titles the fixture sources define.

Code standards for every task: no leading-underscore names anywhere (functions, methods, helpers,
constants, templates); line length 88; no compatibility aliases; Cotton components, never Cotton
template tags.

## Order

**US1 → US2 → US3, one at a time, in the feature worktree** (plan, *Story order*).

---

## US1 — Reach every page from the sidebar (P1)

Issue: #25. Delivers FR-001 – FR-012, FR-014, FR-016, FR-017, FR-019, FR-020; SC-001, SC-004.

### T001 — The Sphinx extension writes the navigation file

**Files**: `mvp_sphinx/navigation.py`, `mvp_sphinx/docs_build.py` (the `NAVIGATION_FILE`
constant only), `pyproject.toml` (deptry DEP004 ignore for `sphinx`, with its reason),
`tests/sphinx/contents/**`, `tests/conftest.py`, `tests/test_navigation.py`

Plan, *The navigation file* and *The extension*. Research R2, R6. New source
`tests/sphinx/contents/` per plan *Tests and fixtures* (`conf.py` lists
`mvp_sphinx.navigation`). `sphinx_json_build` gains a keyword that skips the no-warnings assertion,
used for this source only; a `contents_build` session fixture builds it. Tests (`TestNavigationFile`,
reading the built `navigation.json`): one section per root toctree, in order, captions as given and
`""` for the uncaptioned one (FR-002–FR-004); the hidden toctree's pages are present (FR-006); a
three-deep page chain nests three levels with each `url` the JSON builder's address (FR-005,
FR-010 input); an explicit toctree title wins over the page title (FR-007); the external link and
`self` entries are absent (FR-011); the page listed twice appears at both places and the
back-pointing toctree stops at the repeat (FR-012); the `:orphan:` page is absent; the
markup-character title is stored as the literal text. A build with the `html` builder writes no
navigation file. A root document with no toctree gives `{"sections": []}` (build a tiny source in
`tmp_path`). The file is replaced atomically (no partial file is ever visible at the final name —
assert the write goes through a temporary name, e.g. by checking no stray temp file remains and the
final file parses). Docstrings per `docs/contributing/standards/code-documentation.md`.

### T002 — `DocsBuild.navigation()`

**Files**: `mvp_sphinx/docs_build.py`, `tests/test_docs_build.py`

Plan, *Reading it*. Tests (`TestNavigation`): the contents build's file gives its sections; no file
gives `None`; invalid JSON gives `None`; valid JSON of the wrong shape (top level a list, a section
without `entries`, an entry whose `children` is not a list, a non-string title) gives `None`; an
entry whose `url` is absolute (`"/x/"`), has a scheme or `//` (`"https://example.com/"`,
`"//example.com/"`), contains `..`, or lacks the trailing slash is dropped while its siblings stay;
`""` is kept (the front page listed in a toctree below the root). Module imports nothing from
Sphinx (checked in T003's no-Sphinx test).

### T003 — The contents in the sidebar

**Files**: `mvp_sphinx/menus.py`, `mvp_sphinx/mounted.py`, `tests/sphinx/guide/conf.py`,
`tests/sphinx/handbook/conf.py`, `tests/conftest.py`, `tests/test_menus.py`,
`tests/test_mounted.py`, `tests/test_views.py`

Plan, *The menu* (without the stamp: US1 may rebuild on every `process()`; US3 adds the stamp) and
*Two apps*. Guide and handbook sources gain the extension (their no-warnings builds must stay
clean). A fixture points an app at `contents_build`. Tests, `TestDocumentationMenu` (through
`app.menu.process(request)` with `rf` requests at the app's addresses): top-level order is the front
page entry, then groups and uncaptioned entries in the file's order; a captioned section is a group
named by its caption holding its entries in order; a page with children is a collapsible group whose
first child links to the page itself; every leaf's URL is the mount prefix + the entry's address
(FR-010); the tree is identical when processed for two different page requests (FR-009); a label
with markup characters is a plain `str`, not `SafeString` (FR-014). Through `client`: every sidebar
link on a contents-build page answers 200 and together they cover every page the toctrees list
(SC-001, US1 scenarios 1–7); the markup-character title is escaped in the HTML (FR-014); a page of
the handbook app (at `manuals/admin/`) draws the handbook's contents only, with links under its own
prefix, and a guide page draws none of the handbook's entries (FR-019); with Sphinx blocked in
`sys.modules` (the FS-001 pattern), a page still draws the full contents (US1 scenario 9, FR-017).

### T004 — Documentation, translations and the demo guide

**Files**: `README.md`, `CHANGELOG.md`, `AGENTS.md`, `demo/docs/**`,
`mvp_sphinx/locale/en/LC_MESSAGES/django.po`, `tests/test_demo.py`

README: the one line a host adds to `conf.py` (`extensions = ["mvp_sphinx.navigation"]`), that the
contents appears in the documentation app's sidebar, that Sphinx is still not needed where the site
runs, and what happens without the line (front page entry only). CHANGELOG Unreleased entry.
AGENTS.md: replace "the contents menu and the Sphinx extension are not" with the truth. Demo guide:
`conf.py` gains the extension; `index.rst` gains two captioned toctrees (add a few short pages) and
keeps the tutorials page with its nested page. `django-admin makemessages -l en` for the new
strings. Test (`tests/test_demo.py`): the demo guide's `conf.py` loads the extension (a build of
`demo/docs` into `tmp_path` writes `navigation.json`). Humanize README text (public markdown).

---

## US2 — See where you are (P1)

Issue: #27. Delivers FR-013; SC-002.

### T005 — The current page is marked and its groups open

**Files**: `tests/test_menus.py`, `tests/test_views.py`, `mvp_sphinx/menus.py` (only if a test
exposes a gap)

Plan, *The menu* last paragraph; research R3. Tests on the processed tree for the contents build:
on a page nested inside two groups, that page's leaf is the only selected leaf and both enclosing
groups are selected (scenarios 1–2); on a page with pages of its own, its group is selected and the
leaf for the page itself is the selected leaf (scenario 3); on the front page, the front page entry
is the only selected leaf (scenario 4); on the `:orphan:` page, no item is selected and the tree is
the full contents (scenario 5); on a page listed twice, both of its leaves are selected and no other
(decision D-US2). One test through `client`: the rendered sidebar on a nested page marks exactly the
entries for that page's address as current (the shell's `menu-active` marker is the sidebar's
current-page signal, not a styling choice) and its enclosing `<details>` are open.

---

## US3 — A rebuilt docs build updates the sidebar (P2)

Issue: #28. Delivers FR-015, FR-018; SC-003, SC-005.

### T006 — Rebuild only when the file changed, and see a rebuild at once

**Files**: `mvp_sphinx/menus.py`, `tests/test_menus.py`, `tests/test_views.py`

Plan, *The menu* `refresh()`; research R4, R5. Tests: replacing the navigation file (copy of the
contents build, write a file that adds a page, then one that removes one) shows the change on the
next request with no new app instance (scenarios 1–2, FR-015); processing twice with the file
unchanged does not read it again (patch `DocsBuild.navigation` to count calls); repointing
`build_dir` or processing under a different mount prefix rebuilds; the children are replaced in one
assignment (the new list is complete before it is assigned).

### T007 — No contents, broken contents, no build: pages still served

**Files**: `mvp_sphinx/menus.py` (only if a test exposes a gap), `tests/test_views.py`,
`tests/test_menus.py`, `README.md`

Through `client`: a build made without the extension (copy of a build with `navigation.json`
removed) serves its pages and the sidebar holds only the front page entry (scenario 3); a
`navigation.json` holding invalid JSON, and one of the wrong shape, give the same (scenario 4); with
`build_dir` pointing at a directory that does not exist, and with an unreadable navigation file
(`chmod 000`, skipped when running as root), the demo overview page answers 200 and draws its own
menu (scenario 5, SC-005); a navigation file replaced by garbage mid-run then fixed gives the front
page only and then the full contents again. README: one sentence that a rebuilt docs build shows in
the sidebar on the next request, no restart.
