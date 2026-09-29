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

`build_dir` is read on every request. Rebuild the docs and reload the page to see
the change, with no restart. It doesn't have to exist when the site starts, so a
project that hasn't built its docs yet still boots.

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
