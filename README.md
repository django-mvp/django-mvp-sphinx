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

## Quickstart

Five steps take a project from install to a documentation page in its own
application shell, with the contents in the sidebar and a menu entry that leads
to it. You write no template.

### Before you start

You need a Django project on [django-mvp](https://github.com/django-mvp/django-mvp)
whose application shell already works. This package renders inside django-mvp's
layout and reads its colours from the theme django-mvp supplies, so it does
nothing useful on its own.

You also need a Sphinx source directory for your user guide. The examples call
it `docs/`. If you don't have one yet, Sphinx's own
[`sphinx-quickstart`](https://www.sphinx-doc.org/en/master/usage/quickstart.html)
creates it.

The examples use `yourproject` and `yourapp` for your project's package and one
of its apps. Change those names and the paths to match your own.

### 1. Install

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

### 2. Add the Sphinx line

Add the package's extension to your Sphinx project's `docs/conf.py`:

```python
extensions = ["mvp_sphinx.navigation"]
```

If `conf.py` already lists extensions, add this one to the list.

The extension writes the contents the sidebar shows. Without it the sidebar holds
only the front page's entry, and every page is still served.

### 3. Build the docs

```bash
sphinx-build -b json docs docs/_build/json
```

Sphinx is needed where you run that command and nowhere else. The site that
serves the pages reads the files the build left behind, never imports Sphinx and
never starts a build, so Sphinx can stay out of your production requirements.

The output folder is yours to choose. A build made by a CI step, or one kept
outside your project, works the same way once step 4 points at it. Until a build
exists, every address under the prefix answers 404 and the rest of your site is
unaffected.

### 4. Mount the docs

Create the app once, in a module of its own, and give it the build's folder as
`build_dir`:

```python
# yourproject/mounted.py
from django.conf import settings
from mvp_sphinx.mounted import DocumentationApp

docs = DocumentationApp(build_dir=settings.BASE_DIR / "docs" / "_build" / "json")
```

Then mount it in your URLs under whatever prefix you like:

```python
# yourproject/urls.py
from mvp.mounted import mount

from yourproject.mounted import docs

urlpatterns = [
    mount("docs/", docs),
]
```

### 5. Add the menu entry

Add the app's entry to your menu, in the `menus.py` of one of your installed
apps:

```python
# yourapp/menus.py
from mvp.menus import AppMenu

from yourproject.mounted import docs

AppMenu.append(docs.menu_item())
```

django-flex-menus imports each installed app's `menus` module when Django
starts, which is why the file has to live in an installed app.

### What you now have

Each page of the build answers under `docs/`, drawn by your own `base.html`
inside the application shell. The front page is at `/docs/`, the contents are in
the app sidebar, and your menu has an entry that leads to the front page. The tab
title carries the page's title and the app's `name` (Documentation unless you
change it), and the breadcrumbs lead back through the page's parents to the front
page.

### Changing the docs

Edit your Sphinx source, run the command from step 3 again, and reload the page.
The pages, the contents and the search follow on the next request, with no
restart.

## Using it

Everything below is optional. The quickstart is all a project needs to serve its
documentation.

### The contents in the sidebar

When `sphinx-build -b json` finishes, the extension you added in step 2 of the
quickstart writes a `navigation.json`
into the build with every page your toctrees list, hidden toctrees included.
The documentation app's `menu`, a `DocumentationMenu`, draws it as the sidebar
menu on every page of the docs.

- Each captioned toctree on your front page becomes a group named by its
  caption. An uncaptioned toctree puts its pages at the top level.
- A page with pages of its own opens as a group, and its first entry is the
  page itself.
- The front page has its own entry at the top.
- A page no toctree lists stays out of the sidebar.

Only the JSON builder gets a file, and a build that failed writes nothing.

Rebuild the docs and the sidebar shows the change on the next request, with no
restart.

The extension runs inside your Sphinx build and nowhere else, so the site that
serves the pages still doesn't need Sphinx. Without the line, or with a
`navigation.json` that can't be read, the sidebar holds only the front page
entry and every page is still served.

### The page's own headings

On a wide screen, each page lists its own headings beside it, under "On this
page". The list is nested the way the page nests its sections, and each entry
links to its heading. Sphinx already records that tree in the build, so there is
nothing to configure and the site that serves the pages still doesn't need
Sphinx.

- The page's title is not listed, and neither are the headings of other pages,
  so a front page that only holds a toctree lists nothing from the pages it
  links to. The sidebar keeps the contents.
- A page with no headings below its title shows no list at all.
- Sphinx's `:tocdepth:` setting decides how deep the list goes.

`PageView` reads the tree with `PageHeadings.from_toc(toc)`, which turns a
page's `toc` value from the build into nested dicts of `title`, `anchor` and
`children`. Call it yourself if you draw the headings in a template of your own.

Rebuild the docs and the list follows on the next request.

Every page also ends with links to the page before it and the page after it, in
the order Sphinx puts the pages in, each showing the title of the page it leads
to. The front page has no previous link, the last page has no next link, and a
page that no toctree lists has neither. The links stay inside the documentation
app, so a second app mounted elsewhere links under its own address. An
incremental Sphinx build only rewrites the pages that changed and the pages
whose toctrees changed, so a page's links follow a newly inserted neighbour once
that page is rebuilt. Run a full rebuild (`-E`) if in doubt.

### Search

Every page of a documentation app has a search box. It lists the pages of that
docs build that contain all the words typed, in any order and any case, and finds
other forms of a word too, so `lanterns` finds a page that says "lantern". It
searches that one app's pages and never the rest of your site or another
documentation app. Adding a word narrows the list. Common words such as "the" are
ignored, as Sphinx ignores them.

The page whose title holds all the words comes first, then a page with a section
heading that holds them, then the rest, each group in order of title. Every result
shows the page's title and, when the page's text holds one of the words, a short
passage around it. A result found by a section heading links to that section.

Nothing needs configuring. The search reads the search data Sphinx already writes
into every JSON build (`searchindex.json`), so there is no extra Sphinx setting and
no Sphinx where the site runs. The only extra dependency is `snowballstemmer`, the
stemmer Sphinx itself uses to build that data.

The box is an ordinary form that sends `GET` to the app's `search/` address, for
example `/docs/search/?q=lantern`, so it works with scripts turned off and a search
can be bookmarked or shared. That address is where Sphinx's own search page would
be, so a `:ref:` link to `search` in your docs lands on it. Whoever may read the
pages may search them, under the same `check`.

The `search/` address is reserved under every documentation app, so a folder of your
docs named `search` can't have its own index page there. Name that folder something
else.

The search data is read on each search, so a rebuild is searchable straight away.
A build without it still serves its pages, and the results page says search is
unavailable.

### Naming the documentation

The app's `name` is what the tab title, the first breadcrumb and the menu entry
call the documentation. Give it your own when "Documentation" isn't right:

```python
from django.conf import settings
from django.utils.translation import gettext_lazy as _

docs = DocumentationApp(
    build_dir=settings.BASE_DIR / "docs" / "_build" / "json",
    name=_("Administrator's handbook"),
)
```

### Choosing who can read it

The documentation is open to everyone unless you say otherwise. To keep it for
signed-in people, import `user_is_authenticated` from `flex_menu.checks` and pass
it as `check`:

```python
from django.conf import settings
from flex_menu.checks import user_is_authenticated

docs = DocumentationApp(
    build_dir=settings.BASE_DIR / "docs" / "_build" / "json",
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
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from flex_menu.checks import user_has_any_permission, user_in_any_group

docs = DocumentationApp(
    build_dir=settings.BASE_DIR / "docs" / "_build" / "json",
    check=user_in_any_group("Support"),
)
tickets = DocumentationApp(
    build_dir=settings.BASE_DIR / "tickets" / "_build" / "json",
    name=_("Ticket handling"),
    namespace="tickets",
    check=user_has_any_permission("support.view_ticket"),
)
```

Any function of the request works too:

```python
def staff_only(request):
    return request.user.is_staff


handbook = DocumentationApp(
    build_dir=settings.BASE_DIR / "handbook" / "_build" / "json",
    namespace="handbook",
    check=staff_only,
)
```

A signed-in reader the rule excludes gets your project's 403 page, which says
nothing about the documentation, and no menu entry. The rule alone decides.
Staff and superusers have no way in unless it admits them, and `check=False`
admits no one.

The rule is asked on every request, and often more than once in one, since the
menu entry asks it as well as the page. Keep it quick and free of side effects.
If it raises, the request is a server
error: a page is never served on a guess. The menu entry asks the rule too, so
the error also shows on every page that draws the entry, the sign-in page
included. Write a rule that returns an answer.

A `check` that is not a function is read as yes or no. `check="staff"` is a
non-empty string, which is true, and admits everyone. To keep the docs for
staff, pass `user_is_staff` from `flex_menu.checks`, or a function of your own.

Two audiences are two apps. Each `DocumentationApp` has its own build, `name`,
`namespace` and rule, and each is mounted at its own prefix:

```python
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from flex_menu.checks import user_is_staff

guide = DocumentationApp(
    build_dir=settings.BASE_DIR / "guide" / "_build" / "json",
)
staff_guide = DocumentationApp(
    build_dir=settings.BASE_DIR / "staff_guide" / "_build" / "json",
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
    build_dir=settings.BASE_DIR / "handbook" / "_build" / "json",
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

### Addresses and files served

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

### How pages look and the page template

A `PageView` renders each page, and it finds the page's data through a
`DocsBuild`, which only ever looks inside `build_dir`. To change how a page is
drawn, subclass `PageView` and pass it to your app as `view_class`.

Pages take your site's theme with nothing to configure: the colours are
django-mvp's own, so a page follows the light and dark themes and any theme your
project defines. The package's page template links one stylesheet,
`mvp_sphinx/content.css`, served like the rest of your static files, and only
pages the documentation app renders load it. Sphinx's own stylesheets are never
used.

Before a page is rendered, `BodyRewriter` adds what a stylesheet cannot. It
wraps each table in a scrolling region that takes keyboard focus and is named by
the table's caption, or "Table" when it has none, so a table wider than the
page scrolls sideways for a reader using only a keyboard and a screen reader
announces what the region holds. It also names each heading link (the ¶ Sphinx
puts beside a section heading, a glossary term or a caption) with the link's own
title and the heading's text, such as "Link to this heading: Installing", so a
screen reader tells one link from the next. Everything else in the body reaches
the page exactly as Sphinx wrote it. `PageView` applies it and hands the result
to the template as `body`, so a `PageView` subclass gets it too; to use it elsewhere,
call `BodyRewriter.rewrite(markup)`.

If you override `mvp_sphinx/page.html`, keep `{{ block.super }}` in its `styles`
block so the stylesheet still reaches the page, render `{{ body }}` rather than
`{{ page_data.body }}` so your override keeps the rewrite, and keep the
`mvp-sphinx-content` class on the element that holds it, because every rule in
the stylesheet is scoped to that class. An override of the `content` block also
takes over drawing "On this page" and the previous and next links, which the page
gets as `headings`, `previous_page` and `next_page`. `BodyRewriter.rewrite` returns
a plain string; `PageView` marks it safe because the docs build is your own, and a
caller of its own does the same:

```django
{% extends "mvp_sphinx/page.html" %}
{% load static %}
{% block styles %}
  {{ block.super }}
  <link rel="stylesheet" href="{% static 'yourproject/docs.css' %}">
{% endblock styles %}
```

## Public surface

These are the names a project can use, grouped the way a project meets them.

### Installed app and Sphinx extension

- `mvp_sphinx` is the Django app. Add it to `INSTALLED_APPS` after `mvp`.
- `mvp_sphinx.navigation` is the Sphinx extension. It writes `navigation.json`
  into a JSON build.

### The documentation app

- `mvp_sphinx.mounted.DocumentationApp` serves one docs build under the prefix
  you mount it at. Its keyword options are `build_dir` (required), `name`, `icon`,
  `namespace`, `view_class` and `check`.
- `menu_item()`, inherited from django-mvp's `MountedApp`, returns the entry to
  add to your own menus.
- `menu` is the app's `DocumentationMenu`, which draws the contents as the app
  sidebar.
- Its URL names are `<namespace>:front_page`, `<namespace>:page` (which takes
  `path`) and `<namespace>:search`.

### Views

- `mvp_sphinx.views.PageView` renders a page. Subclass it and pass the subclass as
  `view_class` to change how a page is drawn.
- `mvp_sphinx.views.SearchView` renders the results of a search.

### Building blocks

For a custom view or template:

- `mvp_sphinx.docs_build.DocsBuild` reads a docs build and never looks outside it.
- `mvp_sphinx.menus.DocumentationMenu` turns a build's navigation file into the
  sidebar menu.
- `mvp_sphinx.headings.PageHeadings`, through `PageHeadings.from_toc(toc)`, turns a
  page's `toc` value into nested headings.
- `mvp_sphinx.page_body.BodyRewriter`, through `BodyRewriter.rewrite(markup)`,
  names table regions and heading links in a page body.
- `mvp_sphinx.search.DocsSearch` lists the pages of a build that hold every word
  searched for.
- `mvp_sphinx.search.PageText` gives the text a reader sees in a page body.

### Templates a project may override

- `mvp_sphinx/page.html` draws a page. It receives `body`, `headings`,
  `previous_page`, `next_page`, `search_url` and `page_data`. It has the `styles`
  and `content` blocks, and it holds the page's body in an element with the
  `mvp-sphinx-content` class.
- `mvp_sphinx/search.html` draws the results. It receives `query`, `results` and
  `search_url`, and has the `styles` and `content` blocks. `results` is `None` when
  the build has no search data, and otherwise a list of the pages found, each with
  its `title`, `passage` and `href`.

### Components

Use these in your own templates as `<c-mvp_sphinx.on_this_page />` and so on:

- `mvp_sphinx.on_this_page` draws a page's headings. It takes `headings`.
- `mvp_sphinx.heading_list` draws nested headings as a list. It takes `headings`.
- `mvp_sphinx.page_links` draws the links to the previous and next page. It takes
  `previous` and `next`.
- `mvp_sphinx.search_form` draws the search box. It takes `action` and `query`.

### Static file

- `mvp_sphinx/content.css` is the stylesheet page content uses.

### Settings

There are none. The package reads no Django setting, and everything is configured
on the `DocumentationApp`.

Anything not listed here is internal and may change without notice.

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

### The demo

`demo/` is a Django project on django-mvp's application shell, for looking at this
package in a browser while you work on it. It serves a user guide of its own and a
second guide for staff, each through a documentation app, and the guides between
them hold every state this package draws.

The guides' builds are not committed, so build them before you start the server.
The two `sphinx-build` lines are [step 3 of the quickstart](https://github.com/django-mvp/django-mvp-sphinx#3-build-the-docs) run
on the demo's two sources:

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run sphinx-build -b json demo/docs demo/docs/_build/json
uv run sphinx-build -b json demo/staff_guide demo/staff_guide/_build/json
uv run python manage.py runserver
```

Then open <http://127.0.0.1:8000/docs/> for the user guide. Its sidebar reaches every
page. After you edit a page under `demo/docs/`, run the first `sphinx-build` again and
reload, with no restart. Until a build exists, every address under `/docs/` answers 404.

`seed_demo` made three accounts, all with the password `password`:

- `regular.user@example.com` is signed in but not staff.
- `staff.user@example.com` is staff.
- `super.user@example.com` is a superuser, and staff too.

Only the staff and superuser accounts can open the staff guide at
<http://127.0.0.1:8000/staff-guide/>. Everyone else is asked to sign in or is shown
the forbidden page, and the sidebar has no entry for them. The command refuses to run
unless `DEBUG` is on.

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-sphinx/blob/main/LICENSE).
