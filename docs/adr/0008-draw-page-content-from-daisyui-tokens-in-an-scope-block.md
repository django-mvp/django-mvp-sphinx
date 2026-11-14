# ADR 0008 — Draw page content from daisyUI's tokens in one `@scope` block, without Tailwind's prose styles

**Status:** accepted

Replaces [ADR 0003](0003-style-page-content-with-a-scoped-theme-stylesheet-and-rewrite-only-what-css-cannot.md),
whose rewrite of the page body stands unchanged here.

## Decision

What Sphinx, MyST and sphinx-design write into a page body is styled by one plain-CSS file shipped
in the package, `mvp_sphinx/static/mvp_sphinx/content.css`. The page template links it from the
shell's `styles` block, so only pages a documentation app renders load it. Tailwind's `prose`
styles are not used: no element the package draws carries the `prose` class.

Every rule sits in one block, `@scope (.mvp-sphinx-content) to (.mvp-sphinx-example > :first-child,
.mvp-sphinx-example-pane)`. The rules reach the element that holds the page body and what is inside
it, and stop at a live example's title bar and running page, which keep the host's own styles. The
example's source is code like any other on the page and is styled with it.

The stylesheet writes no colour of its own. Every colour it applies is a daisyUI theme colour
(`var(--color-*)`) or a `color-mix(in oklab, …)` of theme colours, and every colour it makes by
mixing is declared once, on the scope's root, as a `--mvp-sphinx-*` custom property that later
rules read: one set for each meaning of an admonition, one for each kind of version note, the code
colours and the signature surface among them. Radii, border width and field size come from the
theme too (`--radius-box`, `--radius-field`, `--radius-selector`, `--border`, `--size-field`). Each
element is drawn the way daisyUI draws its nearest component: admonitions as soft alerts, code as
mockup-code on the neutral colour, tables in a bordered box, keys as `kbd`, and sphinx-design's
cards, tabs, dropdowns, badges and buttons as card, tabs, collapse, badge and btn.

Space between blocks comes from the stylesheet alone. Browser margins inside the scope are removed,
and one rule spaces any two neighbouring blocks from a few named steps. A heading carries more space
above it than below.

The page sits in django-mvp's `medium` container with "On this page" beside it from the `lg`
breakpoint, and the text is held to a reading width by one `max-width` on the scope's root. The
package writes no layout of its own.

Where the page needs something CSS cannot give, an accessible name or an element that takes keyboard
focus, `BodyRewriter` (`mvp_sphinx/page_body.py`) changes the body before it is rendered, as ADR
0003 decided.

The tests in `tests/test_static/` hold the file to this: no literal colour, every rule scoped to
`.mvp-sphinx-content`, and every text colour the package creates at 4.5:1 or better on the surface
it sits on, in django-mvp's default light and dark themes.

## Why

`prose` styles text for an article set on its own. Its sizes, margins and colours are its own and
do not come from the theme, and the package's stylesheet spent most of its rules undoing them: the
spacing between headings and paragraphs, list items and admonitions was whatever was left when the
two disagreed. Removing it leaves one source for every rule on the page.

A stylesheet that resets margins inside the page body also resets them inside a live example's
title bar, which is drawn with the host's Tailwind utilities. Those utilities sit in a cascade layer
and lose to any unlayered rule, so a prefix selector on every rule could not leave them alone
without an exception written into each one. `@scope` with a lower boundary states the exception
once. Its cost is browser support: Chrome 118, Firefox 146 and Safari 17.4. An older browser drops
the whole block and shows the page with the shell's own styles, readable but unstyled, which the
README states.

Following daisyUI's components rather than a Sphinx theme keeps the promise that pages look like
the rest of the site (Article XIII). The site's own pages are built from those components, and a
reader recognises a tinted alert or a bordered table from the pages around the documentation.

Using django-mvp's container and page layout, rather than widths of the package's own, keeps the
documentation where every other page of the shell sits and leaves the layout to the package that
owns it.

## Revisit if

- django-mvp gives installed apps a way to contribute rules to its own stylesheet, or ships prose
  styles built from the theme's tokens.
- A browser the host projects must support lacks `@scope`.
