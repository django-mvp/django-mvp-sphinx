# Prototype notes: FS-008 Show working examples live next to their source code

This branch carries a working prototype of the screens in `spec.md`. It has no tests and its code
is not the design for the build. These notes say what the screens were drawn against, what they
need, what is faked, and which choices are a matter of taste.

## What exists

- There are no models. A page is read from the docs build on each request (`DocsBuild`), its body
  is passed through `BodyRewriter`, and `PageView` renders it into `mvp_sphinx/page.html`.
- The package's Sphinx extension is `mvp_sphinx.navigation`. It is the one line a host project has
  in its `conf.py`, and until now it only wrote the navigation file.
- Highlighted code already has its look: Sphinx writes `div.highlight` blocks and `content.css`
  colours them from the host's theme. The example's source reuses those blocks unchanged.
- django-mvp supplies the pieces the example is drawn with: DaisyUI tabs, buttons and skeleton,
  `c-alert` for the unavailable notice, and `c-messages` for what a form says after it is sent.
- Nothing in django-mvp shows a page without the application shell around it. That piece was
  missing and the prototype adds a small base template for it.
- Django refuses to show any page in a frame unless the project says otherwise.

## Where to look

Two pages of the demo guide, under "Live examples" in the sidebar:

- "A working form" has the contact form with three source files, and a second example with one
  source file showing part of a template.
- "When an example cannot run" has a slow example, one whose address is gone, one for staff only,
  and one that fails.

## What the screens need from the code

- A marker an author writes in a page's source, naming an address of the site, an optional title
  and one or more source files, each optionally limited to a range of lines.
- The source text and each file's name and language, held in the docs build, in the author's order.
- For each example on a served page: whether the site has a page at its address, without asking
  that page for anything.
- A title for each example. It names the frame for screen readers, so an example without one
  needs a sensible default.
- A way for a page of the site to be shown without the application shell around it, which keeps
  working after a form is posted, after a redirect and after a link inside the example is followed.
- The host project must allow its own pages to be framed by its own site, or the frame stays empty.
  This includes the sign-in and error pages, since those are what a refused or failing example
  shows.
- "Start again" must return the example to its first state with scripts off.
- A build warning for a source file that does not exist, and for an address on another site.
- The example's height. The prototype uses one fixed height and lets a taller example scroll
  inside its frame.

## What the prototype faked

- A page knows it is being shown as an example from `?example=1` on its address. The contact form
  keeps that by posting to its full address and redirecting back to it. A link inside an example
  would lose it and bring the shell back inside the frame.
- The demo's own `base.html` extends a new `mvp_sphinx/base.html` to get the shell-less rendering.
  Whether a host project should have to do that is not decided.
- The demo sets `X_FRAME_OPTIONS = "SAMEORIGIN"` for the whole site.
- The build passes examples to the served page as HTML comments in the page body, found again
  with a regular expression.
- The marker's syntax (`path first-last` per line, relative to the page's file) is a placeholder.
- Source names are bare file names, so two files with the same name in different folders would
  read the same.
- The slow example sleeps for three seconds so the waiting state can be seen.
- The failing example shows Django's debug page, because the demo runs with `DEBUG` on.
- The directive lives in a second module that imports Sphinx. The repository's notes say only one
  module does.
- No translations were added for the new strings, and `CONTEXT.md`, the README and the changelog
  are untouched.
- The demo's existing tests were not run against the two new guide pages.

## What was ruled by eye

Nothing has been reviewed yet. These are the taste choices made so far, each open to change:

- The example and its source sit in one bordered box with a title bar, set apart from the page's
  text.
- Example on the left and source on the right at the widest breakpoint, and stacked with the
  example first below it.
- Several source files are tabs, one visible at a time. A single file shows its name with no tabs.
- "Start again" and "Open on its own" are quiet text buttons in the title bar, with no icons.
- "Open on its own" opens in the same tab.
- The unavailable notice is a soft warning in the example's place, and the title bar then has no
  buttons.
- While an example loads, its place shows the theme's skeleton shimmer at full height.
- The source pane scrolls inside itself once it is taller than the example.
