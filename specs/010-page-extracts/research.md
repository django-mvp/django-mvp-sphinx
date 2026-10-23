# Research: Show a documentation page in the page info dialog

Read against `main` at 4e92da3 and the approved sketch on this branch.

## Planning notes

The spec directory has no `planning-notes.md`. Nothing to answer.

## What the screens need, and how each is met

From `sketch.md`, "What the screens need from the code".

- **One call that names the app, the address and the request.** A method on
  `DocumentationApp`, `page_extract(address, request)`. The developer already holds the app: they
  created it to mount it. A method keeps the reader rule, the build directory and the URL namespace
  on the object that owns them, and needs no second import. The sketch's module-level function is
  dropped.
- **Renders as markup when set as `page_info`, and no icon when there is nothing.**
  `conditional_escape` writes out any object with `__html__` unescaped
  (`django/utils/html.py`, `conditional_escape`), and `<c-mvp.page.info>` draws nothing unless
  `{% if text %}` holds. So the extract is an object with `__html__` and `__str__` returning its
  content, and `__bool__` false when the page holds nothing once its title is gone. A view returns
  `docs.page_extract(...) or ""`, which is what the sketch already does.
- **The content styles inside the dialog, on any host page.** Every rule in
  `mvp_sphinx/static/mvp_sphinx/content.css` is scoped to `.mvp-sphinx-content`, colour roles
  included, so the stylesheet is safe on any page. It reaches the page as a
  `<link rel="stylesheet">` at the start of the content. The HTML standard allows a stylesheet link
  in the body ("body-ok"), and the browser fetches one file however many extracts a page holds.
  The alternative, a block the host fills in its base template, would mean a template of the
  developer's own, which SC-001 rules out. The `prose` class comes from django-mvp's own CSS, which
  every documentation page already relies on.
- **Links and images lead into the documentation app.** Every relative `href` and `src` in the
  content is joined to the page's own address with `urljoin`, the same call `PageView` already uses
  for its neighbour links. A target with a scheme, or one starting with `/`, is left alone. The
  sketch did this with a regular expression. The build does it with `HTMLParser`, recording
  offsets the way `BodyRewriter` does, so only attributes of real start tags are touched.
- **A section with its subsections, without its heading.** Sphinx writes each heading as a
  `<section id="…">` whose first child is the heading. A parser that tracks section depth finds the
  section whose `id` matches the anchor, starts after its heading's end tag, and stops at that
  section's end tag. The page itself is the outermost section, so the same walk with no anchor
  gives the page without its `<h1>`.
- **A warning in the log for a bad address.** `logging.getLogger(__name__)`, the standard library.

## What the sketch faked, and what replaces it

- **Extract code without tests** → rebuilt test-first in `mvp_sphinx/extracts.py`.
- **Regular expression for links** → `HTMLParser` with offsets.
- **Stylesheet link written into the content** → kept, as above. It is now a decision, not a fake.
- **The demo screens** → kept as the demo's own pages. The demo is not distributed, and its screens
  are where the walkthrough happens.

## Settled questions

- **Maths and live examples.** `LiveExamples.parts` already splits a body into markup and examples.
  The extract keeps the markup parts and drops the examples. Maths is left as Sphinx wrote it,
  because typesetting needs `maths.js` and MathJax, which only the documentation app's page loads.
- **What `BodyRewriter` does inside an extract.** It still runs: the table scroll regions and the
  heading link names are wanted in a dialog too.
- **Reader rule.** `MountedApp.has_permission(request)` in the installed django-mvp
  (`mvp/mounted.py`, `has_permission`) answers it, with no redirect or 403, which is what an
  extract needs: it gives nothing instead.
- **Unreadable page file.** `DocsBuild.page` raises `json.JSONDecodeError` or
  `UnicodeDecodeError`, both `ValueError`, or `OSError`. The extract catches those two and gives
  nothing with a warning.
- **The dialog's width** is django-mvp's and not this feature's (django-mvp/django-mvp#592).

## What already exists

- `PageExtract` (the returned object): new code. Nothing in the repo or in django-mvp is a value
  carrying markup, a title and an address. A frozen dataclass from the standard library.
- `DocumentationApp.page_extract`: new code, a method on the existing app.
- Reading the page: this repo, `DocsBuild.page`.
- Reader rule: installed package, `mvp/mounted.py` `MountedApp.has_permission`.
- Page and front page addresses: Django, `reverse` with the app's namespace, as `SearchView.href`
  does.
- Finding a section: new code, an `HTMLParser` subclass. Nothing in the repo finds a section's
  extent. `PageHeadings` reads the `toc` field, which has anchors but no content.
- Rewriting link targets: new code, an `HTMLParser` subclass recording offsets, with
  `urllib.parse.urljoin` from the standard library doing the joining.
- Table regions and heading link names: this repo, `BodyRewriter`.
- Dropping live examples: this repo, `LiveExamples.parts`.
- Title as plain text: this repo, the same `unescape(strip_tags(...))` that `PageView.plain_text`
  does. The plan moves it to a function both use.
- Styles: this repo, `mvp_sphinx/content.css`, unchanged.
- Warnings: the standard library, `logging`.
