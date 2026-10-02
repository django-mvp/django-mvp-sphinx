# AGENTS.md — Agent configuration for django-mvp-sphinx

Serve a project's Sphinx documentation inside its django-mvp application shell.

The package is for reading a docs build the host project has already produced
and serving its pages through a documentation app: the pages render in the host's
shell and theme, and the contents become the app sidebar's menu. Serving never
imports Sphinx. Two modules import Sphinx, both only during a build: the
extension in `mvp_sphinx/navigation.py` that writes the navigation file, and the
`live-example` directive in `mvp_sphinx/live_example.py` that the extension
registers. The `build_docs` management command runs the
build on demand, as a separate process, and imports no Sphinx either. `CONSTITUTION.md` Article XII lists what stays
out of scope. The contents menu is built: the extension in
`mvp_sphinx/navigation.py` writes the navigation file during the build, and
`DocumentationMenu` in `mvp_sphinx/menus.py` draws it as the app sidebar's menu.

## Stack and commands

- **Stack:** Python 3.12+ / Django 5.2, 6.0 and 6.1, uv-managed (hatchling build backend), built on
  django-mvp and django-cotton
- **Install:** `uv sync`
- **Test (whole suite):** `uv run pytest -n auto --dist loadscope`
- **Test (one class or file, while iterating):** `uv run pytest <path> -x` —
  serial, because starting the workers costs more than a focused run takes
- **Lint:** `uv run pre-commit run --all-files`
- **Type-check:** `uv run mypy`
- **Build:** `uv build`
- **Demo project:** `uv run python manage.py runserver 0.0.0.0:8025`
- **Bump the version:** `uv version` — never edit `pyproject.toml` alone, because `uv.lock`
  records this package's own version too

Lint is the pre-commit run rather than a bare `ruff check .`: the hook config
excludes `docs/` and migrations, so a raw invocation reports findings in paths
the gate does not cover, and they cannot be fixed without breaking the ones it
does.

`pre-commit run --all-files` only sees files git knows about. A new file that
has not been added is skipped, and the hooks then reformat it after the commit
that introduced it.

## The demo project

`demo/` is a Django project running on django-mvp's application shell. It is
how this package is looked at while it is being written, and it is never
deployed. Nothing in it is distributed — `pyproject.toml` packages
`mvp_sphinx` alone.

`tests/settings.py` inherits `demo/settings.py` rather than restating it, so
there is one description of the shell.

Everything in the demo fails quietly. A Cotton component that cannot be
resolved renders as empty output, a Tailwind class the packaged stylesheet does
not emit does nothing, and a menu entry whose URL will not resolve is dropped
from the tree. None of them raise, which is why `tests/test_demo.py` asserts
against the rendered page rather than against the objects behind it.

The demo serves its own user guide, whose source is in `demo/docs/`, through a
documentation app mounted at `/docs/`. It is a guide for the demo site's users (signing
in, finding your way, the staff guide, a reference part) and not documentation of this
package, which the README holds. Its sidebar reaches every state the package draws, and
`TestDemoGuideStates` in `tests/test_demo.py` builds it under `-W` and checks each one, so
a page moved or a state dropped fails there. The build is gitignored, so build it before
opening that page and again after editing the guide:

```bash
uv run python manage.py build_docs
```

That is the package's own management command, in
`mvp_sphinx/management/commands/build_docs.py`. It builds both of the demo's guides,
because each app in `demo/mounted.py` names its `source_dir`. `build_docs docs` builds
one. The second guide is the staff guide at `/staff-guide/`. Only staff can read it:
sign in as `staff.user@example.com`.

The guide's Reference part documents `demo/links.py` with `autodoc`, which is why
`demo/docs/conf.py` puts the repository on `sys.path`. Nothing in the site calls that
module. It exists so the guide has reference entries of every kind to draw.

The guide's Examples part has two pages of live examples of the demo's own pages. Their
views are in `demo/examples/views.py`, the form in `demo/examples/forms.py` and the
templates in `demo/templates/demo/examples/`, and the templates extend
`mvp_sphinx/example.html`, so each draws without the shell. The views are:

- `ContactView`, a form that redirects to its own address after a valid post.
- `StatusView`, a page that only shows something.
- `SlowView`, the same page after three seconds, to show the held place. No test
  requests it.
- `StaffNoteView`, open to staff only, to show the sign-in and the refusal.
- `BrokenView`, which raises an error every time.

The demo keeps `X_FRAME_OPTIONS = "SAMEORIGIN"` because Django's default, `DENY`, makes
the browser show nothing in the frame. The second page also names an address the site
does not have, to show the notice. The guide's pages name line ranges of those files, so
a template or view edit that moves lines needs the `.rst` ranges updated with it. The
tests compare each source shown with the lines the page names, so a range that has
drifted still passes them and shows the wrong code; read the two pages after such an edit.

**Adding a page** takes four things: a view in `demo/views.py` on
`mvp.views.MVPTemplateView`, a route in `demo/urls.py`, a template extending
`page_view.html` and filling `{% block page.content %}`,
and a `MenuItem` in `demo/menus.py`.

**Signing in.** `uv run python manage.py seed_demo` creates three accounts —
`regular.user@example.com`, `staff.user@example.com` and
`super.user@example.com`, all with the password `password`. The shell renders
differently for each, so all three exist rather than one. The command refuses
to run unless `DEBUG` is on.

## Components

Components live at
`mvp_sphinx/templates/cotton/mvp_sphinx/<name>.html`.
Cotton maps a tag's first segment onto that directory, so
`<c-mvp_sphinx.page_links>` resolves to
`cotton/mvp_sphinx/page_links.html`.

The directory name is load-bearing and fails quietly: a component Cotton cannot
resolve renders as empty output rather than raising, so renaming the directory
breaks every tag in it without an error anywhere. `tests/test_smoke.py`
asserts the directory exists for that reason.

## Releasing

Releases run through the shared release flow, never by hand and never by
pushing a tag.

1. Dispatch **Prepare Release** with a bump level. It opens a pull request
   carrying the version bump and the CHANGELOG section.
2. Merging that pull request is the release decision. **Tag Release** then cuts
   the tag and the GitHub Release from the merge commit.
3. **Publish** uploads to PyPI through trusted publishing. PyPI binds its
   trusted publisher to the `publish.yml` filename — renaming that file breaks
   publishing until the PyPI project settings are changed to match.

`pyproject.toml` holds the version and is the single source of truth for all
three steps.

**Tag Release skips a version with no matching CHANGELOG section**, which is
what stops the seed version being cut as a release. Leave it under
`## [Unreleased]` until Prepare Release promotes it: writing a `## [0.0.1]`
heading by hand makes the next push to `pyproject.toml` tag and release it.

Two things are needed before the first release: a PyPI trusted publisher for
this project pointed at `publish.yml`, and a `RELEASE_TOKEN` secret that can
write to this repository.

## Agent skills

### Issue tracker

Issues tracked in GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
See `docs/agents/triage-labels.md`.

### Domain docs

One `CONTEXT.md` at the repository root and `docs/adr/` for decisions.
See `docs/agents/domain.md`.

### CI checks

CI runs from the shared reusable workflows in `django-mvp/shared`, pinned at
`v0.6.0`. Because they are called rather than inlined,
their status checks carry the calling job as a prefix. The required checks are:

- `call-build / Code Quality`
- `call-build / Security Scan`
- `call-build / Build Package`
- `call-tests / Test Python 3.12, Django 5.2`
- `call-tests / Test Python 3.12, Django 6.0`
- `call-tests / Test Python 3.13, Django 5.2`
- `call-tests / Test Python 3.13, Django 6.0`
- `call-tests / Test Python 3.12, Django 6.1`
- `call-tests / Test Python 3.13, Django 6.1`

`tests.yml` and `build.yml` deliberately carry no `paths:` filter on
`pull_request`. A required check that is filtered out never reports, and a
check that never reports blocks the merge.

## Working here

Standards and the quality bar live in `CONSTITUTION.md`. The vocabulary to use
in issues, commits and test names lives in `CONTEXT.md`. What the package is
trying to be good at lives in `GOALS.md`, and the order the work happens in
lives in `docs/ROADMAP.md`.
