# django-mvp-sphinx

Serve a project's Sphinx documentation inside its django-mvp application shell.

## Scope & philosophy

django-mvp-sphinx serves a project's Sphinx documentation as pages of the
project itself. The docs render through the project's own templates and theme,
inside its application shell, and their table of contents becomes the app
sidebar. Reading the user guide doesn't mean leaving the application.

It is written first for the people using the application: user guides, how-tos
and reference for the site itself. Developer documentation should work too, but
where the two pull in different directions, the user guide wins.

It serves a Sphinx JSON build (`sphinx-build -b json`). Serving never needs
Sphinx installed and never starts a build: the build is a file the project
produces before a request arrives, however it already does that. A command that
runs the build for you may come later. It does not host documentation for
several projects, keep old versions, or manage translations.

When two designs conflict, the one that makes the docs look like the rest of
the site beats the one that copies a Sphinx theme.

## Installation

```bash
pip install django-mvp-sphinx
```

Then add it to `INSTALLED_APPS`, after `mvp`:

```python
INSTALLED_APPS = [
    # ...
    "mvp",
    "mvp_sphinx",
]
```

This package requires [django-mvp](https://github.com/django-mvp/django-mvp).
It renders inside django-mvp's layout and reads its colours from the theme
django-mvp supplies, so it does nothing useful on its own.

## Usage

Build your Sphinx documentation as JSON, point a `DocumentationApp` at the
folder it writes to, and mount it in your URLs.

```bash
sphinx-build -b json docs docs/_build/json
```

Sphinx is needed where you run that command and nowhere else. The site that
serves the pages reads the files the build left behind and never imports Sphinx,
so it can stay out of your production requirements.

Create the app once, in a module of its own, and give it the build's folder as
`build_dir`:

```python
# yourproject/mounted.py
from mvp_sphinx.mounted import DocumentationApp

from yourproject.settings import BASE_DIR

docs = DocumentationApp(build_dir=BASE_DIR / "docs" / "_build" / "json")
```

Then mount it under whatever prefix you like, and add its entry to your menu:

```python
# yourproject/urls.py
from mvp.mounted import mount

from yourproject.mounted import docs

urlpatterns = [
    mount("docs/", docs),
]
```

```python
# yourproject/menus.py
from mvp.menus import AppMenu

from yourproject.mounted import docs

AppMenu.append(docs.menu_item())
```

Each page of the build now answers under `docs/`, drawn by your own `base.html`
inside the application shell. The tab title carries the page's title and the
app's `name` (Documentation unless you change it), and the breadcrumbs lead back
through the page's parents to the front page.

### The contents in the sidebar

To get the contents, add one line to your Sphinx project's `conf.py`:

```python
extensions = ["mvp_sphinx.navigation"]
```

When `sphinx-build -b json` finishes, the extension writes a `navigation.json`
into the build with every page your toctrees list, hidden toctrees included.
The documentation app's `menu`, a `DocumentationMenu`, draws it as the sidebar
menu on every page of the docs.

- Each captioned toctree on your front page becomes a group named by its
  caption. An uncaptioned toctree puts its pages at the top level.
- A page with pages of its own opens as a group, and its first entry is the
  page itself.
- The front page has its own entry at the top.
- A page no toctree lists stays out of the sidebar.

The extension's `setup` hook connects `write_navigation` to Sphinx's
`build-finished` event, and that hands the finished build to a
`NavigationWriter`, which walks the toctrees and writes the file. Only the JSON
builder gets a file, and a build that failed writes nothing.

The extension runs inside your Sphinx build and nowhere else, so the site that
serves the pages still doesn't need Sphinx. Without the line, or with a
`navigation.json` that can't be read, the sidebar holds only the front page
entry and every page is still served.

### Naming the documentation

The app's `name` is what the tab title, the first breadcrumb and the menu entry
call the documentation. Give it your own when "Documentation" isn't right:

```python
from django.utils.translation import gettext_lazy as _

docs = DocumentationApp(
    build_dir=BASE_DIR / "docs" / "_build" / "json",
    name=_("Administrator's handbook"),
)
```

### Several documentation apps

Each build is one `DocumentationApp` with its own `namespace` (`docs` unless you
say otherwise), mounted at its own prefix, which may have several segments. Each
app serves only its own build and names only itself in its tabs and breadcrumbs.

```python
handbook = DocumentationApp(
    build_dir=BASE_DIR / "handbook" / "_build" / "json",
    name=_("Administrator's handbook"),
    namespace="handbook",
)

urlpatterns = [
    mount("docs/", docs),
    mount("manuals/admin/", handbook),
]
```

Add `handbook.menu_item()` to your menu beside `docs.menu_item()` to give each
its own entry.

A `PageView` renders each page, and it finds the page's data through a
`DocsBuild`, which only ever looks inside `build_dir`. To change how a page is
drawn, subclass `PageView` and pass it to your app as `view_class`.

The images and downloads your pages link to (`_images/` and `_downloads/` in
the build) are served at the addresses the pages already use, with the file's
content type. Nothing else in the build is: not the search index, the page data,
the sources, the static files or Sphinx's pickles. An address that tries to climb
out of those two folders answers 404.

`build_dir` is read on every request. Rebuild the docs and reload the page to see
the change, with no restart. It doesn't have to exist when the site starts, so a
project that hasn't built its docs yet still boots. Until the build exists every
address under the prefix answers 404, the rest of the site is unaffected, and the
first request after the build appears is served.

Addresses behave like the rest of your site. A page address without its trailing
slash redirects permanently to the slashed address, query string kept, and an
address with no page answers your own 404 page. The bare prefix (`/docs`) is
redirected by Django's `CommonMiddleware` (`APPEND_SLASH`), as for any other
mount. A page file that is not valid JSON is a broken build and raises, so it is
a server error rather than a 404.

## Quickstart

<!--
  The smallest complete example: what goes in the view, what goes in the
  template, and what appears on the page. Real code that runs, not a sketch.
  If the example needs three files, show three files.
-->

## Public surface

<!--
  Everything a host project can touch: components and their attributes,
  settings, template tags, models, views. Being able to list it exhaustively is
  a feature of a package this size, and the list is what makes an addition to
  it a deliberate decision rather than a side effect.
-->

## Contributing

Standards for this repository live in
[CONSTITUTION.md](https://github.com/django-mvp/django-mvp-sphinx/blob/main/CONSTITUTION.md),
and the vocabulary to use in issues and commits lives in
[CONTEXT.md](https://github.com/django-mvp/django-mvp-sphinx/blob/main/CONTEXT.md).

```bash
uv sync
uv run pytest
uv run pre-commit install
```

`demo/` is a Django project on django-mvp's application shell, for looking at
this package in a browser while working on it:

```bash
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run python manage.py runserver
```

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-sphinx/blob/main/LICENSE).
