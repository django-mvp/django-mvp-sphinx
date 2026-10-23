# Sketch: Show a documentation page in the page info dialog

## What exists

- `DocsBuild.page(path)` reads a page's JSON from the docs build, confined to the build. Its
  `body` is the page as one `<section>` holding the title's `<h1>` and nested `<section id=…>`
  elements, one per heading. Links and images in it are relative to the page's own address.
- `BodyRewriter` adds the scroll regions round tables and equations and names heading links.
  `LiveExamples.parts` splits a body into markup and live examples.
- `PageView` turns these into a page. Its content styles are `mvp_sphinx/content.css`, scoped to
  `.mvp-sphinx-content` and loaded by `mvp_sphinx/base.html` only.
- `MountedApp.has_permission(request)` answers the documentation app's reader rule.
- django-mvp draws `page_info` in `<c-page.info>`: an info button beside the title opening a modal
  whose heading is the screen's own title. A plain string is escaped, a safe string is written out
  as markup. `page_info_actions` are buttons at the dialog's foot. The modal box is daisyUI's,
  32rem wide, and `<c-page.info>` offers no way to change that.

## What the screens need from the code

- One call that takes the documentation app, the page's address (with a section's anchor or not)
  and the request, and gives back the content, the title and the address in the documentation
  app, or nothing.
- The content renders as markup when it is set as `page_info` as it is, and nothing is drawn
  when there is no extract.
- The page's content styles apply inside the dialog on any screen of the host project.
- Every link and image in the content leads into the documentation app, and links to the page's
  own sections lead to that section of the page.
- A section holds its subsections and leaves out its own heading.
- A warning in the log when the address names no page or no section.

## What the sketch faked

- The extract code in `mvp_sphinx/extracts.py` is written for the sketch, without tests. Its
  link rewriting is a regular expression over `href` and `src` attributes.
- The content styles reach the dialog through a `<link rel="stylesheet">` written into the
  content itself. Whether that is how they get there is for planning.
- The demo screens under "Info dialogs" stand in for a host project's own screens. Their text
  only explains what each one shows.

## What was ruled by eye

Nothing yet.
