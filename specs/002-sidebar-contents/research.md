# Research — 002, the documentation's contents in the app sidebar

Premises the plan rests on, each read from the code the project actually resolves: Sphinx 9.1.0,
sphinxcontrib-serializinghtml 2.0.0, django-mvp 0.25.0 and django-flex-menus 0.4.6 as installed in
the feature worktree's `.venv/lib/python3.13/site-packages/`. Paths below are relative to that
directory.

## R1 — The prototype, and what carries over

`wip/sphinx-docs-in-sidebar` on django-mvp (commit 6da698a) has two pieces this feature needs:
`mvp/integrations/sphinx_view/navigation.py`, a Sphinx extension that walks every toctree from the
root document on `build-finished` and writes `navigation.json`, and `menus.py`, a `Menu` subclass
that rebuilds its children when the file's mtime or the mount's root URL changes. The owner
reviewed it and liked the shape (`runs/django-mvp/sketch-sphinx-view.md`, round 2).

Three things do not carry over as written:

- `menus.py` imports `FILENAME` from `navigation.py`, which imports `sphinx.addnodes` at module
  level. Drawing the menu would therefore import Sphinx, which FR-017 and Article XII forbid. The
  file name moves to a module that imports nothing from Sphinx.
- `refresh()` catches only `FileNotFoundError`; a half-written or malformed file raises
  `json.JSONDecodeError` / `KeyError` from inside the shell's menu walk, which runs on **every**
  host page (R4). FR-018 needs every read failure to fall back to the front page entry.
- The file is written with `write_text`, so a request that lands mid-write reads a truncated file.
  Writing to a temporary file and `os.replace`-ing it makes a replacement atomic on POSIX.

## R2 — What the extension can read at `build-finished`

- `BuildEnvironment.get_doctree(docname)` (`sphinx/environment/__init__.py:650`) returns the
  pickled doctree of any document, including ones not rewritten in an incremental build.
- A `toctree` node's `entries` is a list of `(title, ref)` pairs
  (`sphinx/directives/other.py:127,148,176`). `title` is the explicit title or `None`. `ref` is a
  docname, the literal `'self'`, or an external URL — all three kept as entries (line 147–148).
  Globbed entries are already expanded. `hidden` is a flag on the node (line 75); a hidden toctree
  is still a `toctree` node in the doctree, so walking nodes includes it (FR-006).
- `env.titles[docname]` is the page's title node; `.astext()` is plain text. A ref that is not a
  docname of the build (external URL, missing document) is absent from `env.titles`.
- The JSON builder's addresses: `get_target_uri` (`sphinxcontrib/serializinghtml/__init__.py:68`)
  returns `''` for `index`, `a/` for `a/index`, and `a/b/` for `a/b` — exactly the addresses
  `DocsBuild.page()` serves. The builder's `name` is `'json'` (line 157); `pickle` shares the class
  (line 140) and is not a build this package reads.
- Sphinx itself warns on a self-referencing toctree (`environment/__init__.py:922`), a document in
  several toctrees (line 952) and a circular toctree (`environment/adapters/toctree.py:335`). The
  edge-case fixtures provoke those warnings on purpose, so their build cannot assert "no warnings"
  the way `sphinx_json_build` does today.

## R3 — How the sidebar marks and opens

- `MenuItem.process` (`flex_menu/menu.py:374`) works on a per-request copy; an item with a URL is
  matched by `match_url` (line 596), which for a literal `url` compares normalised paths — query,
  fragment and one trailing slash stripped — against `request.path` (line 628). A parent is
  `selected` when any processed child is (line 428).
- The sidebar draws a leaf with `menu-active` only when `selected`
  (`mvp/templates/cotton/menu/item.html`), and a `MenuCollapse` as `<details open>` when selected
  (`mvp/templates/cotton/menu/group.html`); a `MenuGroup` is a non-clickable section title. So the
  leaf is marked and every group around it opens with no code of ours (FR-013), and a group is
  never itself marked.
- `render_menu` processes a menu once per request and caches it on the request
  (`flex_menu/templatetags/flex_menu.py:66`).
- Labels are drawn with `{{ label }}`, auto-escaped. A plain `str` label shows markup characters as
  text (FR-014) as long as nothing marks it safe.

## R4 — Every host page processes every documentation app's menu

`MountedApp.claiming_menu` (`mvp/mounted.py`, the `for mount_ in cls.mounts(request)` loop)
processes each mounted app's menu on any page no mount served, to find one that claims it. The
contents menu is therefore processed on every host page, not only documentation pages. Reading and
parsing the navigation file there on every request would put a file read and a JSON parse on every
page of the site; a `stat` per request, rebuilding only when the file changed, keeps it to one
system call (the prototype's choice, decisions.md "Rebuilds show on the next request"). A failure
there must never raise, or a broken docs build breaks the host's home page (US3 scenario 5).

## R5 — The Menu is shared across threads

A `Menu` is a module-level singleton registered on flex_menu's global root; `process` copies it per
request but reads `self.children` from the shared instance (`flex_menu/menu.py:437–466`).
Replacing `children` when the file changes is a write to shared state. Assigning a freshly built
list in one statement, after the new tree is fully built, means a concurrent request sees either
the old tree or the new one — the "rebuild in progress" edge case — never a half-built one.

## R6 — Sphinx in the package, but never at runtime

Sphinx stays in the `dev` group (Article XII). The extension module imports `sphinx.addnodes`, so
deptry reports DEP004 (a dev dependency imported by package code). The module only ever runs inside
a Sphinx build the host already runs, so a per-rule ignore naming Sphinx and saying why is the
honest configuration; a runtime dependency would contradict Article XII.
