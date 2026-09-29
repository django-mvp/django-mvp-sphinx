# django-mvp-sphinx

Serve a project's Sphinx documentation inside its django-mvp application shell.

<!--
  The README is this package's charter, and it is read in two places: on the
  repository page and on the package index. Write it for someone deciding
  whether to install this, who has not read anything else here.

  Every link is absolute. A relative link resolves on GitHub and 404s on PyPI,
  which is where the person deciding is most likely to be standing.

  Badges go here once the repository is public — the dynamic ones read the
  GitHub API anonymously and render as "404" or "invalid" against a private
  repository, which looks worse than having none.

  Sections, in this order:
    1. One sentence, above. What it does, for whom.
    2. Scope & philosophy — below. What it is and is not, and the principles
       that settle a close call.
    3. Installation.
    4. Quickstart — the smallest thing that works, end to end.
    5. The public surface, in full. For a package this small, list it.
    6. Anything genuinely surprising: what it deliberately does not do, what it
       leaves to the host project, and the failure modes that are quiet.

  Keep the CHANGELOG out of it. Link to it instead.
-->

## Scope & philosophy

django-mvp-sphinx serves a project's Sphinx documentation as pages of the
project itself. The docs render through the project's own templates and theme,
inside its application shell, and their table of contents becomes the app
sidebar. Reading the user guide doesn't mean leaving the application.

It reads a Sphinx JSON build (`sphinx-build -b json`) and nothing else. It does
not run Sphinx for you, and it does not host documentation for several
projects, keep old versions, or manage translations. Building the docs stays
the project's job, done however the project already does it.

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
