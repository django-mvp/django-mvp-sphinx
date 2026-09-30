# Implementation Plan: Show a page's headings beside it, and links to the previous and next page

**Branch**: `003-page-headings-and-links` | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md) ·
**Research**: [research.md](research.md) · **Tasks**: [tasks.md](tasks.md)

## Summary

Sphinx already writes both pieces into every page's JSON: `toc`, the page's own heading tree as an
HTML fragment, and `prev` / `next`, each a relative link and a rendered title (research R1). The
view reads them from the page data it already loads. A small `PageHeadings` parser turns `toc` into
a heading tree without the page's own title; the previous and next pages are resolved against the
request path the way the FS-001 breadcrumbs are. Two Cotton components of this package draw them:
"On this page" beside the article at wide widths, sticky, and the previous and next links as two
cards below it. Serving still reads files only. This is the reviewed prototype's page layout (R6)
without django-sphinx-view, with the title entry dropped and the layout rebuilt from utilities the
shell's stylesheet emits (R4).

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2 / 6.0 / 6.1

**Primary Dependencies**: django-mvp ≥ 0.25.0 (shell, `c-page`, `c-container`, daisyUI `menu`
classes in its stylesheet), django-cotton. Standard library `html.parser` for the fragment. No new
dependency.

**Storage**: none. The page's `.fjson` file is the only input.

**Testing**: pytest + pytest-django; real Sphinx builds from sources under `tests/sphinx/`, built
once per session; pages requested through `client`.

**Performance Goals**: no extra file read; one parse of a fragment of a few hundred bytes per
request.

**Constraints**: serving never imports Sphinx (FR-011); every link stays under the app's prefix
(FR-008); the list and the links follow the build on disk with no restart (FR-010).

**Scale/Scope**: pages of tens of headings; several documentation apps per host.

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I Testing | Test-first per task; the parser through real builds and plain fragments, the page through `client`. |
| II Simplicity | One parser class, two view methods, three small components. No settings, no cache. |
| III Anti-abstraction | `PageHeadings` subclasses the standard library's `HTMLParser`, the one tool for the job; no base class of our own. |
| IV Integration-first | Acceptance tests request pages and read the markup a browser and assistive technology read: landmarks, names, `href`, `rel`. |
| V Security | Heading and page titles are the host's own build output, marked safe as the page body already is (spec Assumptions; ADR 0001). Nothing from the request reaches the markup except the request path the links are resolved against, which Django has already routed. |
| VI Documentation | README and CHANGELOG in the story that introduces each piece. |
| VII Dependencies | None added. |
| VIII i18n | The list's name and the link labels are `{% trans %}`; catalogue refreshed. |
| IX Data model | No models. |
| X Cohesion | Parsing the fragment is one class; reading the page's headings and neighbours are `PageView` methods beside `get_breadcrumbs` ("a view method instead of a helper the view calls"). |
| XI Compatibility | New names only (`mvp_sphinx.headings.PageHeadings`, three components); nothing removed or renamed. |
| XII Scope | Reads keys of the page JSON; no Sphinx import, no build. |
| XIII Host look | Drawn inside `c-page`/`c-container` with the shell's own utilities and daisyUI `menu`; no Sphinx theme. The contents stay in the sidebar; "On this page" holds headings of the current page only. |

Sam's standing code standards apply to every task: no leading-underscore names anywhere (methods,
helpers, templates, constants, CSS); line length 88; no compatibility aliases; no test of wording or
design preferences (layout, widths); Cotton components written as `<c-…>` components, never through
Cotton's template tags.

No violations. Complexity tracking is empty.

## Design

### The heading tree — `mvp_sphinx/headings.py`

`class PageHeadings(HTMLParser)`: reads the `toc` fragment of one page (research R2) into a list of
headings, each `{"title": SafeString, "anchor": str, "children": [...]}`.

- `@classmethod from_toc(cls, toc: str) -> list[dict]`: the public entry. Feeds the fragment, closes
  the parser, and returns the tree **without the page's own title**: the children of the first
  outer entry, followed by any further outer entries (R2, a page with two top-level sections).
  An empty or missing fragment, a fragment holding only the title, and a title with an empty
  nested list all give `[]`.
- The parser keeps a stack of open lists. `<ul>` opens a list, `<li>` opens an entry in the
  current list, `</li>` and `</ul>` close. The title is **sliced from the fragment, never
  re-emitted**: the parser runs with `convert_charrefs=False` and records the offset just after
  an entry's `<a …>` start tag and the offset of its `</a>`, computed from `getpos()` the way
  `BodyRewriter.position()` does, and the title is `toc[start:end]`, the build's own bytes
  (design review ARCH-001). Sphinx's title filter removes references, so a title holds no nested
  `<a>` (`sphinx/environment/collectors/toctree.py`). The anchor is the `<a>`'s `href` as written
  (`#<id>`). No shared base class with `BodyRewriter` (Article III: one caller each).
- Title markup is wrapped in `mark_safe` with a one-line trust comment and `# noqa: S308`, the
  pattern the view uses for the body: the build is the host's own output (spec Assumptions).
- Names are plain: no leading underscores. Module and class docstrings per
  `docs/contributing/standards/code-documentation.md`.

Why parse rather than inject `toc` whole (the prototype): FR-003 forbids the title entry, the
shell's menu classes must sit on the lists, and "a page with no headings below its title has no
list" (FR-004) becomes `if headings`, true to the tree actually drawn, rather than a second reading
of `display_toc` that can disagree with it (a title holding an empty list, R2).

### The view — `mvp_sphinx/views.py`

`PageView.get_context_data(**kwargs)` calls `super()` and adds three keys, each from a method
beside `get_breadcrumbs`:

- `headings`: `get_headings()` → `PageHeadings.from_toc(self.page_data.get("toc") or "")`.
- `previous_page`, `next_page`: `get_neighbour(key)` for `"prev"` and `"next"` → `None` when
  `page_data.get(key)` is falsy (no key, or Sphinx's `null`), otherwise
  `{"title": mark_safe(title), "href": urljoin(self.request.path, link)}` (research R3). No shape
  validation: Sphinx only ever writes `null` or a `{link, title}` mapping
  (`sphinx/builders/html/__init__.py:572-590`), and `get_breadcrumbs` trusts `parents` the same
  way (design review ARCH-003). Sphinx's general index and search pages carry neither key and get
  neither link.

Nothing is read beyond the page JSON `get()` already loaded, so FR-010 and FR-011 hold with no code
of their own. `get()` is not touched: it passes the rewritten `body` that FS-004 added.
`PageHeadings` follows FS-004's `BodyRewriter` (`mvp_sphinx/page_body.py`): an `HTMLParser`
subclass whose classmethod is the entry point.

### The components — `mvp_sphinx/templates/cotton/mvp_sphinx/`

Annotated per the code-documentation standard (`@description`, `@prop`), like `example.html`.

- `on_this_page.html` — prop `headings`, never empty: `page.html`'s `{% if headings %}` around the
  `<aside>` is the one guard (design review ARCH-002). A
  `<nav>` named by a visible heading through `aria-labelledby` (FR-005: a navigation region with a
  name of its own; the sidebar's list is named by the app's name, so the two differ), holding
  `<c-mvp_sphinx.heading_list :headings="headings" />`.
- `heading_list.html` — prop `headings`. A `<ul>` with one `<li><a href="{{ anchor }}">{{ title
  }}</a>…</li>` per heading and, when the heading has children, a nested
  `<c-mvp_sphinx.heading_list :headings="heading.children" />` inside its `<li>` (FR-001 nesting).
  The outer list carries daisyUI's `menu menu-sm`; nested lists are styled by daisyUI's
  `.menu li > ul` (research R5).
- `page_links.html` — props `previous` and `next`. Renders nothing when both are empty.
  Otherwise a `<nav>` with an `aria-label` of its own (FR-009) holding up to two cards, each an
  `<a href="{{ href }}" rel="prev">` / `rel="next"` naming the page it leads to (FR-006, FR-009),
  with a small "Previous" / "Next" label above the title. The next card stays on the right when
  there is no previous card.

The id the "On this page" heading carries for `aria-labelledby` is fixed (`mvp-sphinx-on-this-page`):
one page renders one list.

### The page — `mvp_sphinx/templates/mvp_sphinx/page.html`

Inside the existing `c-page` / `c-container`: at `xl`, a flex row with a gap; the first column
(`min-w-0 flex-1`) holds the article and, below it, `page_links`; the second, only when there are
headings, is an `<aside>` hidden below `xl` (`hidden xl:block w-56 shrink-0`) whose `nav` is sticky
and scrolls on its own when long (`sticky self-start`, `max-h-[calc(100vh-8.6rem)]
overflow-y-auto`). Only classes the shell's stylesheet emits (R4). Width and offset are judged by
eye at the walkthrough, not tested (spec Assumptions). The `<article class="prose
mvp-sphinx-content py-4">{{ body }}</article>` element FS-004 landed is moved into the first column
unchanged, and the `styles` block that links `content.css` stays as it is.

### Fixtures and tests

- **New source `tests/sphinx/reading/`**, built once per session by `sphinx_json_build("reading")`
  as `reading_build`, with a `reading_app` fixture pointing the demo's app at it (the
  `contents_app` pattern). Pages: a front page with an intro, a section holding a visible toctree,
  and a second section with a sub-section; `long` (sections nested three deep, and a heading holding
  inline code); `single` (exactly one section); `plain` (no section). Four pages in reading order.
  The hidden-toctree and orphan cases use the existing `contents` source (`hidden-page.rst`,
  `orphan.rst`) through `contents_app` (design review ARCH-004).
  Its `conf.py` loads `mvp_sphinx.navigation` so the pages carry contents like the demo's.
- `tests/test_headings.py` (mirrors `mvp_sphinx/headings.py`), `TestPageHeadings`: plain fragments
  and the real build's `toc` values.
- `tests/test_views.py` gains `TestOnThisPage`, `TestPreviousAndNextPage` and
  `TestReadingAfterARebuild`. Elements are found by landmark and name (`nav` by `aria-labelledby` /
  `aria-label`), by `rel`, and by `href`, never by wording.
- No test asserts wording, CSS classes, widths or placement (testing standard; spec Assumptions).

### Demo

`demo/docs/settings.rst` gains one section, the single-entry state. Everything else the walkthrough
needs is already in the demo guide (design review SPEC-001): `content-tour.rst` (FS-004) has
sections nested two deep and a heading holding inline code; `about.rst` has none; the front page is
the first page and Getting started's previous page; About is the last. The demo's reading order is
the front page, Getting started, Tutorials, Your first page, Content tour, Menus, Settings, About.

## Story order

US1 → US2 → US3, sequential, in the feature worktree. US1 and US2 both edit `views.py`,
`page.html` and `tests/test_views.py`; US3 is tests over both. US2 and US3 go out as one dispatch:
US3 adds no production code (FR-010 and FR-011 hold by construction), and its tests need US2's
links on the page.

## Project Structure

```text
mvp_sphinx/
├── headings.py                                   # new: PageHeadings
├── views.py                                      # get_context_data, get_headings, get_neighbour
├── templates/mvp_sphinx/page.html                # two-column layout, both components
├── templates/cotton/mvp_sphinx/on_this_page.html # new
├── templates/cotton/mvp_sphinx/heading_list.html # new
├── templates/cotton/mvp_sphinx/page_links.html   # new
└── locale/en/LC_MESSAGES/django.po
demo/docs/settings.rst                            # one section for the walkthrough
tests/
├── sphinx/reading/                               # new source
├── conftest.py                                   # reading_build, reading_app
├── test_headings.py                              # new
└── test_views.py
README.md, CHANGELOG.md
```

**Structure Decision**: single Django app package, as FS-001 and FS-002 left it.

## Complexity Tracking

None.
