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

### Choosing who can read it

The documentation is open to everyone unless you say otherwise. To keep it for
signed-in people, import `user_is_authenticated` from `flex_menu.checks` and pass
it as `check`:

```python
from flex_menu.checks import user_is_authenticated

docs = DocumentationApp(
    build_dir=BASE_DIR / "docs" / "_build" / "json",
    check=user_is_authenticated,
)
```

That is one import and one keyword. A reader the rule excludes gets no menu
entry and no page. An anonymous visitor is sent to your sign-in page and comes
back to the address they asked for once signed in. The rule covers every address
under the prefix, including the images and downloads your pages link to, and it
answers the same way whatever is behind the address, so a reader cannot tell
which pages exist.

To keep it for a group or for holders of a permission, use the other two
checks from `flex_menu.checks`. Both are factories, so call them with their
arguments:

```python
from flex_menu.checks import user_has_any_permission, user_in_any_group

docs = DocumentationApp(
    build_dir=BASE_DIR / "docs" / "_build" / "json",
    check=user_in_any_group("Support"),
)
tickets = DocumentationApp(
    build_dir=BASE_DIR / "tickets" / "_build" / "json",
    namespace="tickets",
    check=user_has_any_permission("support.view_ticket"),
)
```

Any function of the request works too:

```python
def staff_only(request):
    return request.user.is_staff


handbook = DocumentationApp(
    build_dir=BASE_DIR / "handbook" / "_build" / "json",
    namespace="handbook",
    check=staff_only,
)
```

A signed-in reader the rule excludes gets your project's 403 page, which says
nothing about the documentation, and no menu entry. The rule alone decides.
Staff and superusers have no way in unless it admits them, and `check=False`
admits no one.

The rule is asked on every request. If it raises, the request is a server
error: a page is never served on a guess. The menu entry asks the rule too, so
the error also shows on every page that draws the entry, the sign-in page
included. Write a rule that returns an answer.

A `check` that is not a function is read as yes or no. `check="staff"` is a
non-empty string, which is true, and admits everyone. Pass `user_is_staff`
itself, or a function, to keep the docs for staff.

Two audiences are two apps. Each `DocumentationApp` has its own build, `name`,
`namespace` and rule, and each is mounted at its own prefix:

```python
from django.utils.translation import gettext_lazy as _
from flex_menu.checks import user_is_staff

guide = DocumentationApp(
    build_dir=BASE_DIR / "guide" / "_build" / "json",
)
staff_guide = DocumentationApp(
    build_dir=BASE_DIR / "staff_guide" / "_build" / "json",
    name=_("Staff guide"),
    namespace="staff_guide",
    check=user_is_staff,
)
```

```python
from mvp.mounted import mount

urlpatterns = [
    mount("guide/", guide),
    mount("staff-guide/", staff_guide),
]
```

Each reader sees the entries their rules admit and is served or refused by each
app's own rule. The rule is asked again on every request, so a reader who signs
in or joins a group is admitted by their next request, with nothing to reset.

The rule is django-mvp's `check`, described in its
[mounted apps guide](https://github.com/django-mvp/django-mvp/blob/main/docs/mounted-apps.md#limiting-who-can-reach-an-app).

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
