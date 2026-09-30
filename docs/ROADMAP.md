# Roadmap — django-mvp-sphinx

**Date:** 2026-09-30

This document was designed against [GOALS.md](../GOALS.md). See also [CONTEXT.md](../CONTEXT.md) for domain terminology and [CONSTITUTION.md](../CONSTITUTION.md) for project standards.

## Versioning

Releases are gated on goal importance, not on a count of features.

| Version | Gate |
|---|---|
| `0.0.x` | Building toward the Essential goals. Pre-viable, expect churn, nothing published |
| `0.1.0` | All Essential goals delivered. The minimum usable release, and the first publish |
| `0.1.x` → `0.x` | Advancing the Expected goals, at whatever granularity the work takes |
| `1.0.0` | All Expected goals delivered. The complete, dependable release |
| `1.x` | Stable line: fixes and additive features only |
| `2.0` | The next major, where breaking changes go |

A goal is not one minor release: some take several, and one release can move
two. Once `1.0` ships, a breaking change never goes out as `1.x`. It waits for
the next major.

Aspirational goals may be developed against v2 or v1 as required.

## Essential goals: v0.1.0

Everything needed to reach a minimum usable release.

### R1 — Sphinx pages served in the application shell

*delivered in [#4](https://github.com/django-mvp/django-mvp-sphinx/issues/4) · advances G1, G3*

A host project mounts a `DocumentationApp` at a prefix of its choosing, points it
at its `sphinx-build -b json` output, and every page of that build is a page of the
site: inside the application shell, named in the browser tab, with breadcrumbs
back to the front page. The images and downloads pages link to are served, and
nothing else in the build is. Addresses without a trailing slash redirect,
unknown ones get the site's own 404, a missing build leaves the rest of the site
working, and serving never needs Sphinx installed. A project can name each app
and mount several side by side.

Advances G1 and G3.

### R2 — The contents in the app sidebar

*feature · advances G2, G1*

On every documentation page the app sidebar shows the whole contents, so a
reader can reach any page and can always see where they are. It needs R1's
pages to navigate between.

**Deliverables:**

- Every page reachable from the sidebar, in contents groups named the way the
  docs name them
- A page with pages of its own opens as a group holding them
- The current page marked, and its group open
- "On this page" beside the page on wide screens, listing the page's headings
- Links to the previous and next page at the foot of each page
- A rebuilt docs build shows its new contents without restarting the site

Advances G2 and G1. Out of scope: search, and any navigation outside the
documentation app's own pages.

### R3 — User-guide content looks right in the host's theme

*feature · advances G1, G4*

What a user guide is written with renders as part of the site: every colour
comes from the host's theme, so a theme change or dark mode needs nothing
extra. Unstyled markup would make the pages read as foreign, which is why this
sits in the first release even though its goal is only Expected in full.

**Deliverables:**

- Notes, tips, warnings and the other admonitions, coloured by their meaning
  from the theme
- Highlighted code that follows the theme and dark mode
- Tables that scroll inside the page rather than widening it
- Headings with links a reader can copy, visible on hover and to the keyboard
- Images, figures, glossaries and cross-references displayed as the rest of the
  site displays their kind of content

Advances G1 and G4. Out of scope: API reference pages and maths, which are G9.

### R4 — Adopting it is a mount and one line of config

*resolve · advances G3*

A project new to the package gets from install to a working documentation page
by following the README alone. It comes last in this release because it
describes what R1 to R3 deliver.

**Deliverables:**

- A README quickstart covering install, the one line of Sphinx configuration,
  building the docs, mounting the app and adding its menu entry
- The public surface listed in full in the README
- The demo project serving a user guide of its own, so every state above can be
  looked at in a browser

Advances G3. Out of scope: a command that builds the docs for the project,
which is R7.

## Expected goals: v1.0.0

Everything a complete, dependable release is expected to have.

### R5 — The project decides who can read the docs

*delivered in [#9](https://github.com/django-mvp/django-mvp-sphinx/issues/9) · advances G5*

Each `DocumentationApp` takes a `check`: open to everyone by default,
`user_is_authenticated` for signed-in people only, or a rule of the project's
own, such as a group or a permission. A reader it excludes sees no menu entry
and gets no page, image or download from any address under the app. An
anonymous visitor is sent to sign in and back, a signed-in one gets the site's
403 page, and the answer is the same whatever is behind the address. Two
audiences are two apps, each with its own rule.

### R6 — Search the docs

*feature · advances G6*

A reader can search the documentation's pages from within the documentation
app. Searching the host project's own content is out of scope.

## Aspirational goals: v2.0

Genuine wants that can land in any release once they are ready.

### R7 — Build the docs with a management command

*resolve · advances G7*

A host project can build its docs from its own management commands
instead of calling Sphinx itself. Serving still never runs a build.

### R8 — Live working examples next to their source

*feature · advances G8*

A page can show a working example from the site running live, next to the code
that defines it, so developer documentation can demonstrate rather than only
describe.

### R9 — API reference and maths look right

*feature · advances G9*

Pages generated from code, and pages with mathematical notation, render
properly in the host's theme.
