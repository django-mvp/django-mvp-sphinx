# ADR 0002 — Style page content with one scoped stylesheet built from the theme, and rewrite the body only for what CSS cannot do

**Status:** accepted

## Decision

What Sphinx writes into a page body is styled by one plain-CSS file shipped in the package,
`mvp_sphinx/static/mvp_sphinx/content.css`. The page template links it from the shell's `styles`
block, so only pages a documentation app renders load it. Every selector in it starts with
`.mvp-sphinx-content`, the class on the article that holds the body.

The stylesheet writes no colour of its own. Every colour it applies is a django-mvp theme colour
(`var(--color-*)`) or a `color-mix(in oklab, …)` of two theme colours, and every colour it makes
by mixing is declared once, in the rule on `.mvp-sphinx-content` at the top of the file, as a
`--mvp-sphinx-*` custom property that later rules read. The tests in `tests/test_static/` hold the file to this:
no literal colour, no unscoped selector, and every text and background pair the package creates at
4.5:1 or better in django-mvp's default light and dark themes.

Where the page needs something CSS cannot give, an accessible name or an element that takes
keyboard focus, `BodyRewriter` (`mvp_sphinx/page_body.py`) changes the body before it is
rendered. It records insertions at offsets in the original markup and splices them in. It never
re-emits what it parsed, so everything else reaches the page exactly as Sphinx wrote it.

## Why

A separate package cannot add rules to django-mvp's prebuilt stylesheet, and a Tailwind build of
our own would add a build step here and a second copy of Tailwind's reset to the page. Sphinx
already names everything worth styling with its own classes, so plain CSS keyed off those classes
needs nothing generated. A static file inside an installed app reaches the page through the
staticfiles setup every django-mvp project already has, which keeps the promise that adopting the
package adds no styling step.

Building every colour from the theme's custom properties means a page follows a theme change and
dark mode with nothing to configure. Declaring the created colours in one place makes the promise
checkable from the file alone, which matters because the obvious choices fail it: the theme's
status colours used directly as code-token colours measured under 2.2:1 on the light code
background. Mixing them toward the theme's own text colour fixes both themes at once.

A script could add the names and focus instead, but it would put JavaScript on every page. A
build-time Sphinx extension would only reach hosts that load it. Re-emitting parsed HTML token by
token altered bare ampersands, references without a semicolon and tag case, and splicing into the
original leaves those untouched by construction.

## Revisit if

- django-mvp gives installed apps a way to contribute rules to its own stylesheet, or ships
  code-token colour roles of its own.
- The package gains a Sphinx extension every host is required to load; the rewrite could then move
  into the build.
