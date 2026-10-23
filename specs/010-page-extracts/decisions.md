# Decisions: Show a documentation page in the page info dialog

Rationale too long to sit in the spec, and the choices made while specifying it.

## D1. Sections and the full-page link are in, a template tag is out

The idea arrived with three possible additions: extracts of one section, a button in the dialog
leading to the full page, and a template tag. The first two are in.

- Sections are in because authors write a guide for readers, not for dialogs. A guide that covers several
  screens on one page could not feed their dialogs without them, short of splitting the page.
- The full-page link needs nothing beyond the extract's address, which the extract carries
  anyway. Django-mvp's `page_info_actions` already draws the button.
- The template tag is out. The use that prompted the feature is a view setting `page_info`,
  which a tag does not help with. A view can already pass an extract to any template, so a tag would
  be a second way of doing the same thing. It can be added later if a project needs extracts in
  templates that have no view of their own.

**ADR:** none — a scope choice for this feature

## D2. A bad address logs a warning instead of raising

The host page must render whatever happens to the documentation, so a missing page gives no
extract. That also hides a mistyped address. Raising for a mistyped address and staying quiet for a
missing build is not possible, because the two look the same on disk: a page that is absent may
never have existed or may not have been built yet. A warning is the one signal that works for both.

**ADR:** none — local to this feature, nothing else inherits it

## D3. A new glossary term

"Page extract" joins `CONTEXT.md` when the feature is built: the content of a page, or of one of
its sections, shown outside the documentation app. It is the word the issue and the spec use.

**ADR:** none — vocabulary, recorded in CONTEXT.md

## D4. The design review's findings were all applied

Six findings, none blocking. Each was a small edit to the plan: links are checked by fetching them,
since the catch-all route resolves anything; an extract with no text and no image is false; a
section title keeps its entity references; a test runs with Sphinx blocked; the extract logic lives
in the app's method, with no second public function; and a section's link to a sibling section is
tested.

**ADR:** none — corrections to this feature's plan

## D5. The content carries its own stylesheet link

An extract can appear on any page of the host project, and those pages do not load the
documentation app's stylesheet. The content starts with a `<link rel="stylesheet">` to it, which
HTML allows in the body. The alternative, a block the host fills in its own base template, would
make the developer write a template, which the spec rules out. Every rule in the stylesheet is
scoped to `.mvp-sphinx-content`, so loading it on another page changes nothing outside the extract,
which is what ADR 0003 already establishes.

**ADR:** none — follows from ADR 0003's scoped stylesheet; it adds no new principle
