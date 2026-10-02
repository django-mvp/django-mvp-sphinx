# Prototype: API reference pages and maths

A prototype of the screens in `spec.md`, built to be looked at in a browser before the feature is
planned. It has no tests of its own and it is not the implementation. The markup and styles a
reviewer approves are kept. Everything behind them is rebuilt, test-first, when the feature is
built.

## Where to look

Build the demo guide with `uv run python manage.py build_docs`, run the demo project, and open the
guide's Reference part.

- **Link helpers** (`/docs/reference/link-helpers/`) is the API reference page. It documents a
  small module, `demo/links.py`, and holds a summary table, functions, a constant, an exception, a
  function with a long signature, a function with no description, a deprecated function, and a
  class with attributes, a class method, a property, methods and a class nested inside it.
- **How long a page takes to read** (`/docs/reference/reading-time/`) is the maths page. It holds
  maths inside sentences, two numbered equations with references to them, an equation wider than
  the page, a matrix, maths inside a note and a table, and one formula with a mistake in it.
- The same maths page with `?typeset=off` added to its address shows how it reads before the maths
  is typeset, or when it cannot be.
- Following `[source]` on any entry opens the module's source listing.

Each is worth opening in the light and the dark theme, and at a phone's width.

## What exists

- **The page body is styled by one stylesheet.** `mvp_sphinx/static/mvp_sphinx/content.css` holds
  every rule under `.mvp-sphinx-content`, makes each colour once at the top from the theme's own
  colours, and is checked by `tests/test_static/` for literal colours, unscoped selectors and
  contrast (ADR 0003). Code blocks, tables, admonitions, version notes and heading links are
  already styled there, so they needed nothing inside a reference entry.
- **The host's own text styling reaches definition lists.** Its `prose` class makes every `dt`
  semi-bold and indents every `dd`. Sphinx writes reference entries and their field lists as
  definition lists, so the prototype starts from that and overrides it.
- **Heading links already cover signatures.** The existing rule reveals a link when its `dt` is
  pointed at, `BodyRewriter` (`mvp_sphinx/page_body.py`) already gives it an accessible name from
  the text before it, and every element with an `id` already clears the top bar when followed.
- **Tables are already wrapped in a scrolling region** that takes keyboard focus, so the summary
  table gets that for free.
- **Sphinx marks maths and leaves it for the browser.** With its default settings the body holds
  the author's notation inside `span.math` and `div.math`, and a numbered equation carries its
  number and a heading link in a `span.eqno`. Nothing in the docs build typesets it.
- **The view knows the body before it renders.** `PageView` holds the page's markup, so it can
  tell whether a page has maths.
- **Source listings are served already.** The pages Sphinx writes under `_modules/` are ordinary
  pages of highlighted code.

## What the screens need from the code

- A page needs to know whether its body holds maths, so that only those pages load anything for
  typesetting it.
- Typesetting has to be limited to what Sphinx marked as maths. A dollar sign or a backslash in a
  code sample must be left alone.
- An equation wider than the page scrolls inside its own area. That area has to be reachable and
  scrollable from the keyboard, and it needs an accessible name. The prototype relies on the
  typesetting library making each equation focusable and does not name the area.
- The heading link inside an equation's number needs an accessible name that says which equation
  it links to. Today it is named from the text before it, which for an equation is only its number.
- An entry's heading link is named from the whole signature, parameters included. A shorter name,
  the object's own name, would read better to a screen-reader user.
- The stylesheet's contrast check has to cover the new pairs: signature text, keywords, default
  values and muted parts on the signature's background, and field labels on the page background.
- The source listing page needs its "back to documentation" links looked at. They are shown, but
  nothing in this feature styles the listing beyond what code blocks already get.
- The README has to say what a host project gets for reference pages and maths, and anything it
  must know about where the typesetting comes from.

## What the prototype faked

- **Where the typesetting comes from.** The maths page loads MathJax 4 from the jsDelivr CDN, the
  address Sphinx itself uses by default. Whether the package ships it, the host project serves it
  or the reader's browser fetches it is undecided, and a documentation app on a closed network
  would show untypeset maths with this prototype.
- **The check for maths** is a search of the body for `class="math`. It would also match a code
  sample that contains those characters.
- **`?typeset=off`** exists only so the untypeset state can be looked at without turning scripts
  off. It is not part of the feature.
- **The typesetting settings** are a small script, `mvp_sphinx/static/mvp_sphinx/maths.js`, loaded
  before the library. Nothing checks that it loads first under every host configuration.
- **A failed formula's colour** overrides the typesetting library's own red-on-yellow with the
  theme's error colour. It has not been checked for contrast.
- **Only Python entries are shown.** Other languages use the same markup, but none is in the demo.
- **`demo/links.py`** exists only to give the demo guide something to document. Nothing in the
  site calls it.

## What was decided by eye

These are choices where nothing but looking settles it. Each is open to change in review, and the
build keeps whatever is approved.

- A signature is a bar in the code block's background and font, with the documented name in bold,
  the module path and return arrow muted, and keywords such as `class` and `property` in the
  keyword colour. No other part of a signature is coloured.
- A long signature wraps between its parts, with later lines hanging under the first, and does not
  scroll sideways.
- An entry's description hangs from a thin rule under the signature. A nested entry sits inside
  that rule, so each level of nesting adds one rule. The indent shrinks on a narrow screen.
- Parameters, returns and raised errors are stacked: a small muted label in capitals, then the
  items beneath it without bullets, each parameter name in the code font.
- An entry with no description shows its signature alone, with no rule beneath it.
- The entry a link leads to is outlined in the theme's primary colour, as is a numbered equation
  reached by its reference.
- `[source]` sits at the end of the signature's last line, in the page's ordinary font.
- An equation on its own line is centred, with its number at the end of the line in the muted
  colour.
- Before typesetting, and without it, the author's notation is shown in the code font.

Settled by a rule and not by eye:

- Every colour is one the stylesheet already makes from the theme (Constitution Article XIII).
- Wide content scrolls inside its own area and the page never scrolls sideways (WCAG 1.4.10).
- Revealing the link on a signature uses the existing heading-link rule, which already honours a
  reader's request for reduced motion.
