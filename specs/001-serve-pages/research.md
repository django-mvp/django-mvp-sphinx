# Research — 001 Serve Sphinx documentation pages inside the application shell

**Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

## R1. What `sphinx-build -b json` writes

Probed with Sphinx 9.1.0 on a four-document project (front page with inline code in its title, a
top-level page, a sub-folder index, a page nested two folders deep, an image, a `:download:`).

- One `<docname>.fjson` per document. `index.rst` → `index.fjson`, `sub/index.rst` →
  `sub/index.fjson`, `sub/deep/leaf.rst` → `sub/deep/leaf.fjson`.
- Links between pages are **relative and slash-terminated**: from the front page `one/`,
  `sub/`, `sub/deep/leaf/`; from `sub/index` the previous link is `../one/`. A folder's index
  document is linked as the folder (`sub/`), never as `sub/index/`. So a page must be served at
  its slashed address or every relative link in its body is off by one segment.
- Each page carries `title` (HTML: `Front <code class="docutils literal notranslate"><span
  class="pre">page</span></code>`), `body` (HTML, opening with the document's own `<h1>` inside
  a `<section>`, with a `¶` header link), `parents` (list of `{link, title}`, relative, root
  excluded: `sub/deep/leaf` has `[{"link": "../../", "title": "Sub"}]`), `prev`, `next`, `toc`,
  `display_toc`, `current_page_name` and several Sphinx-internal keys.
- Images are copied to `_images/<name>` and referenced relatively from the body. Downloads are
  copied to `_downloads/<hash>/<name>`.
- The build directory also holds `globalcontext.json`, `searchindex.json`, `environment.pickle`,
  `objects.inv`, `last_build`, `.buildinfo`, `.doctrees/`, `_sources/*.txt` and `_static/`.
  `genindex.fjson` and `search.fjson` are ordinary page files (D12).

## R2. The prototype and the dependency it drops

`wip/sphinx-docs-in-sidebar` on django-mvp (`mvp/integrations/sphinx_view/`) subclassed
django-sphinx-view's `DocumentationView`. That view is 30 lines: it 404s any path without a
trailing slash, then tries `<path>index.fjson` and `<path minus slash>.fjson` under the build
directory, with no check that the result stays inside the build. The prototype added a
`_images`/`_downloads` file branch confined with `resolve()` + `is_relative_to()`, a permanent
slash redirect, tab title and breadcrumbs with markup stripped, and a `DocumentationApp` on
django-mvp's `MountedApp`.

This package owns that behaviour directly (docs/brainstorm.md, CONSTITUTION Article XII). What
carries over: the `MountedApp` shape, the two-candidate lookup order, the file branch and its
containment check, stripping markup from titles. What changes: the page lookup gets the same
containment check as files; the slash redirect fires only when the slashed address has a page
(R5); parent links are made absolute; the contents menu and navigation extension stay out (#5).

## R3. django-mvp's mounted apps (0.25.0)

`mvp.mounted.MountedApp` takes keyword overrides only for attributes the class declares, builds
its menu entry with `menu_item()` (current on every page of the app), and `mount(route, app)`
wraps `include(app.urls)`. The shell reads `mounted_app` into the tab title as
`<block title> | <app name> | <site>` and draws `page.breadcrumbs` in the app header.

`MountedApp.claiming_menu` calls `app.menu.process(request)` on every host page no mount serves,
so every documentation app needs a real `flex_menu.Menu`, never `None`. `flex_menu.Menu`
attaches itself to the global root by name, so the name must be unique per app. It is derived
from the app's namespace.

Two mounts with the same instance namespace make `reverse()` ambiguous (Django warns with
`urls.W005`), so each documentation app has its own `namespace`, defaulting to `docs`.

## R4. The page heading and the shell's title

`page_view.html` draws `c-page.title`, an `<h1>`. The page body already opens with Sphinx's own
`<h1>`, so the documentation template does not extend `page_view.html` and draws no
`c-page.title`: it extends `base.html` and fills `content` with `c-page` + `c-container` + the
body, as the prototype did. `page.title` is still set, for the tab. django-mvp's stylesheet
already emits `.prose`, which gives the body readable defaults without any styling of Sphinx's
own markup (that is #7).

## R5. Addresses

- Django's `APPEND_SLASH` redirects only when the slashed address resolves. The documentation
  app's catch-all route resolves everything, so the view decides: it redirects a slashless
  address only when the slashed one has a page, and otherwise answers not found (FR-009, FR-010).
  `request.get_full_path(force_append_slash=True)` keeps the query string.
- `<path:path>` captures percent-decoded text, so `..` segments arrive as-is. Every lookup is
  `resolve()`d and checked with `is_relative_to()` against its own root: the build for pages, the
  `_images`/`_downloads` folder for files. `resolve()` follows symlinks, so a link pointing out of
  the folder is refused too. A path with a NUL byte raises `ValueError` from the filesystem calls,
  which the lookup answers as not found.
- A page is only ever read as `.fjson` and rendered through the template. No other build file is
  returned as a file, whatever its name (FR-008).

## R6. Sphinx in the development environment only

Tests build real docs with Sphinx (Article IV: exercise the package the way a host does, and the
fixture then cannot drift from what Sphinx writes). Sphinx goes in the `dev` dependency group,
which the shared CI workflow installs with `uv sync`. The package itself never imports it:
`deptry` confirms nothing in `mvp_sphinx` needs it, and a test serves every page with `sphinx`
blocked in `sys.modules` (FR-013, SC-003).
