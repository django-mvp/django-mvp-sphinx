# Implementation Plan: Show a documentation page in the page info dialog

**Branch**: `010-page-extracts` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Prototype**: [sketch.md](sketch.md)

## Summary

A documentation app gains one method, `page_extract(address, request)`, returning a
`PageExtract` or `None`. The extract holds the page's body, or one section of it, without its
heading, with every relative link and image pointed into the documentation app, wrapped in the
documentation app's content styles. A view sets it as `page_info` and puts its `url` in a
`page_info_actions` button. Nothing about how the documentation app serves its own pages changes.

The approved sketch's screens are kept: the demo's "Info dialogs" pages, the dialog as django-mvp
draws it, the "Open the full page" button. The code behind them, `mvp_sphinx/extracts.py`, is
rebuilt test-first.

## Technical Context

- Python 3.13, Django 6.x, django-mvp as locked. No new dependency.
- Serving never imports Sphinx (Article XII). Tests build their docs with Sphinx, as every other
  test module does.
- Files: `mvp_sphinx/extracts.py` (new), `mvp_sphinx/mounted.py` (one method),
  `mvp_sphinx/views.py` (`plain_text` moves out), `tests/test_extracts.py` (new),
  `tests/sphinx/extracts/` (new fixture source), `tests/conftest.py`, the demo, `README.md`,
  `CHANGELOG.md`, `CONTEXT.md`.

## Constitution Check

- **XII Scope.** Read from the docs build on disk, on every call, without Sphinx. One build per app.
  Pass.
- **XIII Pages look like the host project.** The extract carries the same content styles, every
  colour from the host's theme. The dialog is django-mvp's own. Pass.
- **Testing standard.** Tests assert links, ids, presence and absence, permissions and logged
  warnings. No wording, no classes beyond the `mvp-sphinx-content` hook the stylesheet depends on.
  Pass.

## The extract

`mvp_sphinx/extracts.py` holds:

- **`PageExtract`**, a frozen dataclass: `content` (a `SafeString`), `title` (plain text), `url`
  (the address in the documentation app, with `#anchor` for a section). `__str__` and `__html__`
  return `content`. `__bool__` is false when the extracted markup was empty or whitespace before
  it was wrapped, so `extract or ""` gives no icon (spec, Edge Cases).
- **`SectionFinder(HTMLParser)`**: given a body and an anchor (`""` for the page), records the
  offset after the end tag of the matching section's first heading, the offset of that section's
  own end tag, and the heading's text. The section is the first `<section>` when the anchor is
  empty, otherwise the `<section>` whose `id` equals the anchor. Section depth is counted so a
  nested section's end tag never ends the outer one. The heading text skips the `a.headerlink`
  inside it. Offsets come from `getpos()` and line starts, as in `BodyRewriter`. Not found → both
  offsets `None`.
- **`LinkRewriter(HTMLParser)`**: records the offset and length of every `href` and `src`
  attribute value on a start tag (and a self-closing tag) whose value is relative: no scheme, no
  network location, not starting with `/`. `rewrite(markup, base)` splices `urljoin(base, value)`
  in, every other byte as written. Values are joined as Sphinx wrote them, entity references
  included, so `&amp;` in a query stays `&amp;`.
- **`extract_page(app, address, request)`**: the whole job, in this order.
  1. `app.has_permission(request)` false → `None`, nothing logged.
  2. Split the address at the first `#` into path and anchor.
  3. `DocsBuild(app.build_dir).page(path)`. `ValueError` or `OSError` → warning, `None`. `None` →
     warning, `None`.
  4. `SectionFinder` on the body. Not found → warning, `None`.
  5. The page's address: `reverse(f"{namespace}:page", kwargs={"path": path})`, or
     `reverse(f"{namespace}:front_page")` for the empty path.
  6. Slice the body, rewrite links against the page's address, run `BodyRewriter`, keep only the
     markup parts of `LiveExamples.parts`.
  7. Wrap with `format_html`: the stylesheet `<link>` from `static("mvp_sphinx/content.css")`,
     then `<div class="prose mvp-sphinx-content">` holding the markup.
  8. Title: the section heading's text for a section, otherwise the page's `title` as plain text.
     `url`: the page's address, plus `#anchor` for a section.
- Warnings use `logging.getLogger(__name__)` and name the app's namespace and the address as
  given.

`DocumentationApp.page_extract(self, address, request)` in `mounted.py` returns
`extract_page(self, address, request)`. One public way in, documented on the method.

`PageView.plain_text` becomes `plain_text()` in `extracts.py`, imported by `views.py`, so the
title is made plain the same way in both. No alias is left behind.

## The demo

The sketch's demo views stay, rewritten to call `docs.page_extract(...)`. `InfoDialogView`
caches the extract per request and returns `extract or ""` from `get_page_info`, and one action
from `get_page_info_actions` when there is an extract. The five screens, their URLs and their menu
group are kept exactly as approved.

## Fixtures and tests

A fixture source, `tests/sphinx/extracts/`, built once per session like the others
(`extracts_build`, `extracts_app` in `tests/conftest.py`):

- `index.rst`: a toctree of the pages below, and one paragraph.
- `screens.rst`: a title, an opening paragraph, three sections, the second holding a subsection.
  Links to another page (`:doc:`), to its own third section (`:ref:`), an image from the guide's
  `pixel.png` (copied in), a table, inline and displayed maths. The opening paragraph links to a
  subsection.
- `other.rst`: a short page the links lead to.
- `toc-only.rst`: a title and a toctree with no text.

Live examples need the directive's configuration and a running example, so the live-example case
reuses `examples_build` and its app.

`tests/test_extracts.py`, classes by subject:

- `TestPageExtract`: content holds the opening paragraph and every section; no `<h1>`; title and
  url; front page at `""`; rebuilt build read on the next call (write a new `.fjson` into a copy).
- `TestExtractLinks`: every `href`/`src` in a page extract resolves (`resolve()` on the path) to
  the documentation app's page or file view, own-section links carry the page's address and anchor,
  external links unchanged. Parser unit tests on `LinkRewriter` for a `/`-rooted value, a scheme, a
  self-closing tag and an attribute-looking string inside text.
- `TestSectionExtract`: holds its subsection, not the sections around it, no heading of its own,
  title from the heading, url with the anchor, unknown anchor → `None` and a warning.
- `TestReaderRule`: `staff_guide_app`-style app with `user_is_staff`: anonymous and regular users
  get `None`, staff get the extract.
- `TestNothingToShow`: missing build, missing page, address without its trailing slash, `..` in the
  address, unreadable file → `None`, no exception; warnings logged (`caplog`) for the page,
  section and unreadable cases; toc-only page gives a false extract.
- `TestExtractContent`: the `mvp-sphinx-content` wrapper and the stylesheet link are present;
  maths markup kept; live examples dropped from an `examples_build` page.
- `TestInfoDialog` in `tests/test_demo.py`: each demo screen renders 200; the whole-page and
  section screens hold `#pageInfoModal` and the extract's links; the staff screen has no dialog for
  anonymous and regular users and has one for staff; the moved screen has no dialog; the action
  button's `href` is the extract's url.
- `TestDocumentationApp` gains nothing: `page_extract` is covered through the tests above, called
  as a developer would call it.

## Story order

US1 → US3 → US2 → US4, one implementer, sequentially, in the feature worktree. All four stories
touch the same module and the same test file, so splitting them across worktrees would only add
merges. The tasks are ordered so each leaves the tree green.

## Risks

- Sphinx puts extra `id`s on `<span>` targets for labels. An anchor naming one of those is not a
  section and gives `None`, as the spec says. Watch item for the walkthrough, not a change.
- A host whose CSS lacks the `prose` class would show unstyled typography. django-mvp ships it, and
  documentation pages already depend on it.
