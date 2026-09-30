# Research — 005 README quickstart

Premises read from origin/main at f8d30be (FS-001 to FS-004, FS-006, FS-007 merged), django-mvp
0.25.0 and django-flex-menus 0.4.6 as installed in the development environment.

## R1. The package's public names today

Module-level public names in `mvp_sphinx/`:

- `mounted.DocumentationApp` (attributes `name`, `icon`, `namespace`, `build_dir`, `view_class`,
  `urls`, plus `check` and `menu_item()` from django-mvp's `MountedApp`). URL names under its
  namespace: `front_page`, `search`, `page` (path converter `path`).
- `views.PageView`, `views.SearchView`.
- `docs_build.DocsBuild`, `menus.DocumentationMenu`, `headings.PageHeadings`,
  `page_body.BodyRewriter`, `search.DocsSearch`, `search.PageText`.
- `navigation`: `NavigationWriter`, `write_navigation`, `setup`. The module is the Sphinx
  extension, and these three are what Sphinx calls.
- `apps.MvpSphinxConfig`.
- Templates: `mvp_sphinx/page.html`, `mvp_sphinx/search.html`. Components under
  `cotton/mvp_sphinx/`: `heading_list`, `on_this_page`, `page_links`, `search_form`, and
  `example`, the cookiecutter's starter.
- Static: `mvp_sphinx/content.css`.
- No setting is read (`grep settings mvp_sphinx/*.py` finds none).

`example.html` is a placeholder. Its description says "Replace it with the first real component".
`tests/test_smoke.py::TestStarterComponent` says "Delete this class along with the starter component
it covers", and the demo overview's "The starter component" section is the only use.

## R2. How a host's menu entry gets registered

`flex_menu.apps` calls `autodiscover_modules("menus")` in `ready()`, so every installed app's
`menus` module is imported at start-up. The demo imports its own `menus` explicitly in
`DemoConfig.ready` as well. A quickstart `menus.py` therefore works in any installed app with no
further wiring, and does not work in a package that is not an installed app. That is why the README
says "one of your installed apps".

## R3. A missing build, and a rebuild

`DocumentationApp.build_dir` is read per request (FS-001). With no build on disk, every address
under the prefix answers 404 and start-up is unaffected (README, *Several documentation apps*).
A rebuild into the same folder is served on the next request, contents included, because
`DocumentationMenu` re-reads `navigation.json` when its modification time changes (FS-002).

## R4. The demo guide today

`demo/docs/` holds the states US3 names, most of them on `content-tour.rst`: nine admonition
kinds, a generic and a nested one, `seealso`, version notes, four highlighted blocks, a plain block,
a wide table and a table in a list, a long code line, a scaled image and a figure, a glossary with
`:term:` references. `getting-started.rst` has an image and a `:download:` of `notes.txt`.
`tutorials/` is the nested branch. The front page has two captioned hidden toctrees and one
uncaptioned one. The prose, however, is about the package ("The extension writes the guide's
contents into the build"), which spec decision 3 rules out. The rewrite is of voice and page
arrangement. The states are already all present.

## R5. The prototype's guide

`demo/sphinx_docs/` on django-mvp `wip/sphinx-docs-in-sidebar` (246 lines): a guide for an invented
inventory site with *Getting started* (a nested *Signing in*), *Guides* (products, importing, a page
with a very long title) and *Reference* (settings, glossary). It is a model for shape and voice. Its
subject is not the demo site, so its text is not reused.
